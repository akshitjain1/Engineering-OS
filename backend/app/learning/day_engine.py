"""Builds and runs one day of study as an ordered, resumable session.

Design decisions worth knowing
------------------------------
1. Two independent cursors, not one.
   The old planner walked a single 449-topic chain, so DSA (Domain 2) sat behind
   52 Java topics and could never be reached. Here CORE and DSA advance
   separately. DSA gets a block every day, weekday or weekend.

2. Prerequisites are advice, not a gate.
   `evaluate_prerequisites` is still used, but only to attach a "you may want to
   review X first" hint. Nothing is hidden. See `curriculum.ENFORCE_PREREQUISITES`.

3. Budget is filled top-down with floors.
   Each block declares a floor and a target. Blocks are added in priority order
   at their floor first, then grown toward target with leftover minutes. This
   removes the old under-fill (150 of 180 minutes) and stops the planner from
   emitting three blocks on the same trivial topic.

4. Every block must answer: what, where, how long, why.
   A block without a resolved resource URL is downgraded rather than shipped
   blind, because "open source not mapped" is the main reason the app felt
   untrustworthy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    CurriculumLesson,
    CurriculumResource,
    CurriculumTopic,
    RevisionSchedule,
)
from app.learning import service
from app.learning.day_models import (
    ACTIVITY_BUILD,
    ACTIVITY_DSA,
    ACTIVITY_LEARN,
    ACTIVITY_PRACTICE,
    ACTIVITY_REFLECT,
    ACTIVITY_REVIEW,
    OPEN_STATUSES,
    STATUS_ACTIVE,
    STATUS_DONE,
    STATUS_PENDING,
    STATUS_SKIPPED,
    DailyPlanItem,
    DayJournal,
)
from app.learning.streak import local_today, record_activity

DEFAULT_USER = "akshit"
DSA_DOMAIN = "dsa"

# Blocks that must never be dropped to fit the budget.
NON_DROPPABLE = {ACTIVITY_LEARN, ACTIVITY_DSA, ACTIVITY_REFLECT}


@dataclass
class BlockSpec:
    activity_type: str
    title: str
    subtitle: Optional[str]
    why: str
    how: str
    floor_minutes: int
    target_minutes: int
    topic: Optional[CurriculumTopic] = None
    resource: Optional[CurriculumResource] = None
    resource_kind: Optional[str] = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_utc(value: Optional[datetime]) -> Optional[str]:
    """Always hand the browser an explicit UTC instant.

    SQLite drops tzinfo on DateTime columns, so a bare isoformat() would be
    read as local time in the browser and the elapsed-time clock would jump.
    """
    if value is None:
        return None
    aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return aware.astimezone(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Resource resolution (bulk, no N+1)
# ---------------------------------------------------------------------------

_ROLE_PREFERENCE = {
    ACTIVITY_LEARN: ("PRIMARY", "SUPPLEMENT", "REFERENCE"),
    # Practice must not fall back to the study video. Reopening the same URL
    # is not practice, and pretending it is was one reason the plan felt fake.
    # With no practice source the block falls back to the topic's own questions.
    ACTIVITY_PRACTICE: ("PRACTICE",),
    ACTIVITY_DSA: ("PRACTICE", "PRIMARY"),
    ACTIVITY_BUILD: ("PRACTICE", "DEEP_DIVE"),
}


def resources_for_topics(
    db: Session, topic_ids: Iterable[int]
) -> dict[int, list[CurriculumResource]]:
    """One query for every resource attached to the given topics."""
    ids = [tid for tid in topic_ids if tid]
    if not ids:
        return {}
    rows = db.execute(
        select(CurriculumLesson.topic_id, CurriculumResource)
        .join(CurriculumResource, CurriculumResource.lesson_id == CurriculumLesson.id)
        .where(CurriculumLesson.topic_id.in_(ids))
        .order_by(CurriculumResource.order_index)
    ).all()
    grouped: dict[int, list[CurriculumResource]] = {}
    for topic_id, resource in rows:
        grouped.setdefault(topic_id, []).append(resource)
    return grouped


def pick_resource(
    resources: list[CurriculumResource], activity_type: str
) -> Optional[CurriculumResource]:
    """Best usable resource for a block: visible, has a URL, not broken."""
    usable = [
        r
        for r in resources
        if (r.url or "").startswith("http")
        and (r.verification_status or "") != "BROKEN"
        and (r.learner_visible in (None, 1, True))
    ]
    if not usable:
        return None
    order = _ROLE_PREFERENCE.get(activity_type, ("PRIMARY",))
    usable = [r for r in usable if (r.role or "PRIMARY").upper() in order]
    if not usable:
        return None

    def rank(resource: CurriculumResource) -> tuple[int, int, int]:
        role = (resource.role or "PRIMARY").upper()
        role_rank = order.index(role) if role in order else len(order)
        exact_rank = 0 if (resource.exactness or "") == "EXACT" else 1
        verified_rank = (
            0
            if (resource.verification_status or "") in ("VERIFIED", "VERIFIED_COVERAGE")
            else 1
        )
        return (role_rank, verified_rank, exact_rank)

    return sorted(usable, key=rank)[0]


# ---------------------------------------------------------------------------
# Cursors
# ---------------------------------------------------------------------------


def _spine(db: Session) -> list[CurriculumTopic]:
    return [
        topic
        for topic in service.ordered_topics(db)
        if (getattr(topic, "topic_type", "LEARNABLE") or "LEARNABLE") == "LEARNABLE"
    ]


def cursors(
    db: Session,
    user_id: str = DEFAULT_USER,
    exclude_topic_ids: Optional[set[int]] = None,
) -> tuple[Optional[CurriculumTopic], Optional[CurriculumTopic], dict[str, bool]]:
    """Return (core_topic, dsa_topic, completion_index).

    CORE skips the DSA domain so the two lanes never fight over the same slot.

    ``exclude_topic_ids`` skips topics regardless of completion state. extend_day
    uses it to find the next *uncovered* topic, so asking for more time advances
    past whatever today already scheduled -- even if the learner never ticked the
    "finished this topic" box. Passing None behaves exactly as before.
    """
    completion = service.topic_completion_index(db, user_id)
    skip = exclude_topic_ids or set()
    core: Optional[CurriculumTopic] = None
    dsa: Optional[CurriculumTopic] = None
    for topic in _spine(db):
        domain = (getattr(topic, "domain_key", None) or "").lower()
        done = bool(completion.get(topic.slug))
        if done or topic.id in skip:
            continue
        if domain == DSA_DOMAIN:
            if dsa is None:
                dsa = topic
        elif core is None:
            core = topic
        if core is not None and dsa is not None:
            break
    return core, dsa, completion


# ---------------------------------------------------------------------------
# Day template
# ---------------------------------------------------------------------------


def day_mode(plan_date: str) -> str:
    return "weekend" if date_cls.fromisoformat(plan_date).weekday() >= 5 else "weekday"


def _prereq_hint(topic: CurriculumTopic, completion: dict[str, bool]) -> str:
    """Advisory only. Never blocks."""
    refs = topic.prerequisites or []
    missing: list[str] = []
    for ref in refs:
        slug = ref.get("slug") if isinstance(ref, dict) else ref
        if slug and not completion.get(slug):
            missing.append(str(slug))
    if not missing:
        return ""
    head = ", ".join(missing[:2])
    return f"Optional warm-up if you feel lost: {head}."


# LEARN targets are calibrated for first-time learning. When the learner is
# re-covering material they already know, that overshoots -- so LEARN drops to
# ~60% and DSA, which is genuinely new material, takes the surplus. PRACTICE and
# REFLECT are unchanged: retrieval and reflection cost the same either way.
LEARN_TARGET = {"weekday": 35, "weekend": 45}
LEARN_TARGET_REVISION = {"weekday": 20, "weekend": 28}
DSA_TARGET = {"weekday": 40, "weekend": 60}
DSA_TARGET_REVISION = {"weekday": 55, "weekend": 80}

# Pass-2 stretch ceiling as a multiple of target. DSA is allowed to absorb more
# in revision mode because that is where the spare capacity should land.
DSA_STRETCH = 1.5
DSA_STRETCH_REVISION = 2.0
LEARN_STRETCH = 1.5


def build_blocks(
    db: Session,
    *,
    budget_minutes: int,
    plan_date: str,
    user_id: str = DEFAULT_USER,
    exclude_topic_ids: Optional[set[int]] = None,
    cycle_only: bool = False,
) -> list[BlockSpec]:
    """Today's blocks.

    ``cycle_only`` builds just the teaching cycle -- LEARN + PRACTICE for the
    CORE cursor and one DSA block -- with no REVIEW, BUILD, REFLECT or leftover
    filler. That is what extend_day appends: one more lap, not a second day.
    """
    mode = day_mode(plan_date)
    core, dsa, completion = cursors(db, user_id, exclude_topic_ids)
    due_reviews = [] if cycle_only else service.pending_revisions(db, user_id)
    revision = bool(service.get_or_create_study_settings(db, user_id).revision_weighted)

    topic_ids = [t.id for t in (core, dsa) if t]
    resources = resources_for_topics(db, topic_ids)

    blocks: list[BlockSpec] = []

    if due_reviews:
        titles = ", ".join(str(item.get("title") or "item") for item in due_reviews[:3])
        blocks.append(
            BlockSpec(
                activity_type=ACTIVITY_REVIEW,
                title=f"Recall {len(due_reviews)} due item{'s' if len(due_reviews) > 1 else ''}",
                subtitle=titles,
                why="Spaced recall before new material. Skipping this is how earlier topics quietly rot.",
                how="Close the notes. Say the explanation out loud, then grade yourself Hard / OK / Easy.",
                floor_minutes=8,
                target_minutes=15 if mode == "weekday" else 20,
            )
        )

    if core:
        resource = pick_resource(resources.get(core.id, []), ACTIVITY_LEARN)
        hint = _prereq_hint(core, completion)
        blocks.append(
            BlockSpec(
                activity_type=ACTIVITY_LEARN,
                title=core.name,
                subtitle=(getattr(core, "domain_key", None) or "core").upper(),
                why=("Next topic in your main track. " + hint).strip(),
                how="Watch or read once at normal speed. Then write the idea in your own words in three lines.",
                floor_minutes=20 if revision else 25,
                target_minutes=(LEARN_TARGET_REVISION if revision else LEARN_TARGET)[mode],
                topic=core,
                resource=resource,
                resource_kind="study",
            )
        )
        practice_resource = pick_resource(resources.get(core.id, []), ACTIVITY_PRACTICE)
        blocks.append(
            BlockSpec(
                activity_type=ACTIVITY_PRACTICE,
                title=f"Practice: {core.name}",
                subtitle="Questions and exercises for the topic you just studied",
                why="Retrieval on the same day is what turns a video into knowledge.",
                how="Answer the topic questions from memory first. Look things up only after you have tried.",
                floor_minutes=10,
                target_minutes=20 if mode == "weekday" else 25,
                topic=core,
                resource=practice_resource,
                resource_kind="practice",
            )
        )

    # DSA runs every single day, on its own cursor, independent of the core track.
    if dsa:
        dsa_resource = pick_resource(resources.get(dsa.id, []), ACTIVITY_DSA)
        blocks.append(
            BlockSpec(
                activity_type=ACTIVITY_DSA,
                title=f"DSA: {dsa.name}",
                subtitle="Daily pattern block",
                why="DSA compounds only with daily reps. It runs on its own track, so it never waits on anything else.",
                how="Learn or revise the pattern, then solve two problems. Write the approach before writing code.",
                floor_minutes=25,
                target_minutes=(DSA_TARGET_REVISION if revision else DSA_TARGET)[mode],
                topic=dsa,
                resource=dsa_resource,
                resource_kind="pattern",
            )
        )

    if mode == "weekend" and not cycle_only:
        hint = service._available_project_hint(db, user_id)
        if hint:
            blocks.append(
                BlockSpec(
                    activity_type=ACTIVITY_BUILD,
                    title=hint.get("title") or "Build session",
                    subtitle="Project work",
                    why="Weekend build slot. Applying the week's topics is what makes them stick and gives you something to show.",
                    how="Pick the next milestone. Commit something small that runs before you stop.",
                    floor_minutes=30,
                    target_minutes=60,
                )
            )

    if cycle_only:
        return _fit_to_budget(
            blocks, budget_minutes, revision=revision, allow_filler=False
        )

    blocks.append(
        BlockSpec(
            activity_type=ACTIVITY_REFLECT,
            title="Close the day",
            subtitle="Two minutes of writing",
            why="A short written recap is the cheapest way to find out what you did not actually understand.",
            how="Answer three prompts: what I learned, where I got stuck, what I do first tomorrow.",
            floor_minutes=5,
            target_minutes=8,
        )
    )
    return _fit_to_budget(blocks, budget_minutes, revision=revision)


def _fit_to_budget(
    blocks: list[BlockSpec],
    budget: int,
    *,
    revision: bool = False,
    allow_filler: bool = True,
) -> list[BlockSpec]:
    """Floors first, then grow toward target. Non-droppable blocks always survive."""
    budget = max(30, int(budget))
    kept: list[BlockSpec] = []
    used = 0
    for block in blocks:
        if used + block.floor_minutes <= budget or block.activity_type in NON_DROPPABLE:
            kept.append(block)
            used += block.floor_minutes
        # else: dropped for today, no error raised

    minutes = {id(b): b.floor_minutes for b in kept}
    leftover = budget - used

    # Pass 1: grow every block to its target, in priority order.
    for block in kept:
        if leftover <= 0:
            break
        grant = min(max(0, block.target_minutes - minutes[id(block)]), leftover)
        minutes[id(block)] += grant
        leftover -= grant

    # Pass 2: spend anything still left on the two blocks that reward extra
    # time most, capped at a multiple of target so a big budget cannot produce a
    # two-hour single block that nobody will actually sit through. In revision
    # mode DSA gets a higher ceiling -- it is the first-time material.
    dsa_stretch = DSA_STRETCH_REVISION if revision else DSA_STRETCH
    # DSA before LEARN so the surplus reaches the block that should absorb it.
    stretchable = [b for b in kept if b.activity_type == ACTIVITY_DSA]
    stretchable += [b for b in kept if b.activity_type == ACTIVITY_LEARN]
    for block in stretchable:
        if leftover <= 0:
            break
        multiplier = dsa_stretch if block.activity_type == ACTIVITY_DSA else LEARN_STRETCH
        cap = int(block.target_minutes * multiplier)
        grant = min(max(0, cap - minutes[id(block)]), leftover)
        minutes[id(block)] += grant
        leftover -= grant

    for block in kept:
        block.floor_minutes = minutes[id(block)]

    # Anything still unspent becomes a real extra block rather than silently
    # vanishing. The old planner reported "150 of 180" and left you guessing.
    if leftover >= 25 and allow_filler:
        kept.insert(
            max(0, len(kept) - 1),
            BlockSpec(
                activity_type=ACTIVITY_PRACTICE,
                title="Extra reps",
                subtitle="Spare capacity today",
                why=f"You budgeted {budget} minutes and the core blocks only needed {budget - leftover}.",
                how="Pick one: more DSA problems on today's pattern, or re-derive this week's hardest topic from a blank page.",
                floor_minutes=leftover,
                target_minutes=leftover,
            ),
        )
    return kept


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _serialize(item: DailyPlanItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "position": item.position,
        "activity_type": item.activity_type,
        "title": item.title,
        "subtitle": item.subtitle,
        "why": item.why,
        "how": item.how,
        "topic_id": item.topic_id,
        "topic_slug": item.topic_slug,
        "domain": item.domain,
        "resource": (
            {
                "id": item.resource_id,
                "title": item.resource_title,
                "provider": item.resource_provider,
                "url": item.resource_url,
                "kind": item.resource_kind,
            }
            if item.resource_url
            else None
        ),
        "planned_minutes": item.planned_minutes,
        "actual_minutes": item.actual_minutes,
        "status": item.status,
        "started_at": _iso_utc(item.started_at),
        "completed_at": _iso_utc(item.completed_at),
        "note": item.note,
    }


def generate_day(
    db: Session,
    *,
    budget_minutes: Optional[int] = None,
    user_id: str = DEFAULT_USER,
    timezone_name: Optional[str] = None,
    force: bool = False,
) -> dict[str, Any]:
    """Create today's session. Idempotent unless `force`.

    Regeneration preserves completed work: finished blocks are kept and only
    open blocks are replaced. Losing a morning's progress to an accidental
    "Regenerate" click is exactly the kind of thing that stops you trusting it.
    """
    plan_date = local_today(timezone_name)
    existing = (
        db.query(DailyPlanItem)
        .filter(DailyPlanItem.user_id == user_id, DailyPlanItem.plan_date == plan_date)
        .order_by(DailyPlanItem.position)
        .all()
    )
    if existing and not force:
        return get_day(db, user_id=user_id, timezone_name=timezone_name)

    settled = [i for i in existing if i.status in (STATUS_DONE, STATUS_SKIPPED)]
    for item in existing:
        if item.status in OPEN_STATUSES:
            db.delete(item)
    db.flush()

    mode, resolved = service.plan_mode_and_budget(
        db, minutes=budget_minutes, timezone_name=timezone_name, user_id=user_id
    )
    spent = sum(i.planned_minutes for i in settled)
    blocks = build_blocks(
        db,
        budget_minutes=max(30, resolved - spent),
        plan_date=plan_date,
        user_id=user_id,
    )

    position = max((i.position for i in settled), default=-1) + 1
    settled_keys = {(i.activity_type, i.topic_id) for i in settled}
    for block in blocks:
        key = (block.activity_type, block.topic.id if block.topic else None)
        if key in settled_keys:
            continue  # already done or deliberately skipped today
        db.add(_item_from_block(block, user_id=user_id, plan_date=plan_date, position=position))
        position += 1
    db.flush()
    return get_day(db, user_id=user_id, timezone_name=timezone_name, mode=mode)


def _item_from_block(
    block: BlockSpec, *, user_id: str, plan_date: str, position: int
) -> DailyPlanItem:
    topic = block.topic
    resource = block.resource
    return DailyPlanItem(
        user_id=user_id,
        plan_date=plan_date,
        position=position,
        activity_type=block.activity_type,
        title=block.title,
        subtitle=block.subtitle,
        why=block.why,
        how=block.how,
        topic_id=topic.id if topic else None,
        topic_slug=topic.slug if topic else None,
        domain=(getattr(topic, "domain_key", None) if topic else None),
        resource_id=resource.id if resource else None,
        resource_title=resource.title if resource else None,
        resource_provider=resource.provider if resource else None,
        resource_url=resource.url if resource else None,
        resource_kind=block.resource_kind,
        planned_minutes=block.floor_minutes,
    )


CURRICULUM_EXHAUSTED = "You have reached the end of the curriculum."


def extend_day(
    db: Session,
    *,
    minutes: int = 60,
    user_id: str = DEFAULT_USER,
    timezone_name: Optional[str] = None,
) -> dict[str, Any]:
    """Append one more teaching cycle to today. Never rebuilds, never deletes.

    generate_day(force=True) cannot do this job: it excludes every
    (activity_type, topic_id) that already settled today, so on a finished day
    every candidate block is filtered out and the rebuild yields nothing. This
    instead asks the cursors for the next topic *not already covered today*, so
    it advances whether or not the learner marked the current topic finished.
    """
    plan_date = local_today(timezone_name)
    existing = (
        db.query(DailyPlanItem)
        .filter(DailyPlanItem.user_id == user_id, DailyPlanItem.plan_date == plan_date)
        .order_by(DailyPlanItem.position)
        .all()
    )

    covered = {i.topic_id for i in existing if i.topic_id}
    core, dsa, _completion = cursors(db, user_id, covered)
    if core is None and dsa is None:
        day = get_day(db, user_id=user_id, timezone_name=timezone_name)
        day["first_new_item_id"] = None
        day["message"] = CURRICULUM_EXHAUSTED
        return day

    blocks = build_blocks(
        db,
        budget_minutes=minutes,
        plan_date=plan_date,
        user_id=user_id,
        exclude_topic_ids=covered,
        cycle_only=True,
    )
    if not blocks:
        day = get_day(db, user_id=user_id, timezone_name=timezone_name)
        day["first_new_item_id"] = None
        day["message"] = CURRICULUM_EXHAUSTED
        return day

    position = max((i.position for i in existing), default=-1) + 1
    added: list[DailyPlanItem] = []
    for block in blocks:
        item = _item_from_block(
            block, user_id=user_id, plan_date=plan_date, position=position
        )
        db.add(item)
        added.append(item)
        position += 1

    # Keep REFLECT as the closing block in the rail rather than stranding it in
    # the middle of the day. Only ever one REFLECT: cycle_only does not add one.
    for item in existing:
        if item.activity_type == ACTIVITY_REFLECT:
            item.position = position
            position += 1

    db.flush()
    day = get_day(db, user_id=user_id, timezone_name=timezone_name)
    day["first_new_item_id"] = added[0].id if added else None
    day["message"] = None
    return day


def get_day(
    db: Session,
    *,
    user_id: str = DEFAULT_USER,
    timezone_name: Optional[str] = None,
    mode: Optional[str] = None,
) -> dict[str, Any]:
    plan_date = local_today(timezone_name)
    items = (
        db.query(DailyPlanItem)
        .filter(DailyPlanItem.user_id == user_id, DailyPlanItem.plan_date == plan_date)
        .order_by(DailyPlanItem.position)
        .all()
    )
    serialized = [_serialize(item) for item in items]
    current = next(
        (i for i in serialized if i["status"] == STATUS_ACTIVE),
        next((i for i in serialized if i["status"] == STATUS_PENDING), None),
    )
    planned = sum(i["planned_minutes"] for i in serialized)
    logged = sum(i["actual_minutes"] for i in serialized)
    done = sum(1 for i in serialized if i["status"] == STATUS_DONE)
    journal = (
        db.query(DayJournal)
        .filter(DayJournal.user_id == user_id, DayJournal.entry_date == plan_date)
        .first()
    )
    return {
        "plan_date": plan_date,
        "mode": mode or day_mode(plan_date),
        "items": serialized,
        # The read path never writes. An empty day tells the caller to generate;
        # only /today acts on it, so opening a catalog page creates nothing.
        "needs_generation": not serialized,
        "current_item_id": current["id"] if current else None,
        "totals": {
            "planned_minutes": planned,
            "logged_minutes": logged,
            "items_total": len(serialized),
            "items_done": done,
            "complete": bool(serialized) and done + sum(
                1 for i in serialized if i["status"] == STATUS_SKIPPED
            ) == len(serialized),
        },
        "journal": (
            {
                "learned": journal.learned,
                "struggled": journal.struggled,
                "tomorrow": journal.tomorrow,
            }
            if journal
            else None
        ),
    }


def _get_item(db: Session, item_id: int, user_id: str) -> DailyPlanItem:
    item = db.get(DailyPlanItem, item_id)
    if not item or item.user_id != user_id:
        raise LookupError(f"plan item {item_id} not found")
    return item


def start_item(db: Session, item_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    item = _get_item(db, item_id, user_id)
    if item.status == STATUS_PENDING:
        item.status = STATUS_ACTIVE
        item.started_at = _now()
    db.flush()
    return _serialize(item)


#: Activities that represent learning a topic, and so feed the revision queue.
#: PRACTICE and REFLECT do not -- practice is retrieval on material the LEARN
#: block already queued, and REFLECT is not topic-bound at all.
REVISABLE_ACTIVITIES = {ACTIVITY_LEARN, ACTIVITY_DSA}

#: First review lands tomorrow. This is REVISION_INTERVALS[0], which is also
#: what service.revision_interval(0.0) returns -- a topic with no assessment
#: evidence yet has no measured confidence.
FIRST_REVIEW_DAYS = 1


def _enqueue_revision(db: Session, item: DailyPlanItem, user_id: str) -> None:
    """Put a just-finished topic into the spaced-review queue.

    Nothing else fed this queue: service.complete_topic deliberately never
    touches revision schedules, and the only other entry point was a manual
    "Add to review" click. So the Revise leg of Learn -> Practice -> Build ->
    Revise never ran, and early topics decayed while the learner was deep in
    DSA.

    Scheduling itself is service._upsert_revision -- the same function the
    mastery path uses. No second scheduler.

    An existing row is left exactly as it is. Idempotency is the stated
    requirement, but the reason to skip rather than re-upsert is spacing: a
    topic that has already earned a 30-day interval must not be knocked back
    to tomorrow just because its LEARN block came round again.
    """
    if item.activity_type not in REVISABLE_ACTIVITIES or not item.topic_id:
        return
    existing = (
        db.query(RevisionSchedule)
        .filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.item_id == item.topic_id,
            RevisionSchedule.item_type == "topic",
        )
        .first()
    )
    if existing is not None:
        return
    service._upsert_revision(
        db,
        item.topic_id,
        0.0,
        user_id,
        _now(),
        FIRST_REVIEW_DAYS,
    )
    db.flush()


def complete_item(
    db: Session,
    item_id: int,
    *,
    minutes: Optional[int] = None,
    note: Optional[str] = None,
    complete_topic: bool = False,
    user_id: str = DEFAULT_USER,
) -> dict[str, Any]:
    """Finish a block and hand back the next one. This is the routing hop
    the UI needs so the user is never dropped back on a dashboard."""
    item = _get_item(db, item_id, user_id)
    item.status = STATUS_DONE
    item.completed_at = _now()
    item.actual_minutes = int(minutes if minutes is not None else item.planned_minutes)
    if note:
        item.note = note
    db.flush()

    if complete_topic and item.topic_id:
        service.complete_topic(db, item.topic_id, user_id)
        # Never let a bad revision row block marking work as done. Finishing a
        # block is the user's action; the queue is bookkeeping behind it.
        try:
            _enqueue_revision(db, item, user_id)
        except Exception:  # noqa: BLE001
            pass

    # Logging here is what makes the streak real. Previously nothing in the
    # daily plan ever wrote a LearningActivity row, so the streak never moved.
    record_activity(
        db,
        activity_type=item.activity_type.lower(),
        minutes=item.actual_minutes,
        source="day_session",
        local_date=item.plan_date,
        user_id=user_id,
    )

    return {"item": _serialize(item), "next": _next_open(db, item, user_id)}


def skip_item(
    db: Session, item_id: int, *, reason: Optional[str] = None, user_id: str = DEFAULT_USER
) -> dict[str, Any]:
    item = _get_item(db, item_id, user_id)
    item.status = STATUS_SKIPPED
    item.completed_at = _now()
    item.note = reason
    db.flush()
    return {"item": _serialize(item), "next": _next_open(db, item, user_id)}


def _next_open(
    db: Session, item: DailyPlanItem, user_id: str
) -> Optional[dict[str, Any]]:
    nxt = (
        db.query(DailyPlanItem)
        .filter(
            DailyPlanItem.user_id == user_id,
            DailyPlanItem.plan_date == item.plan_date,
            DailyPlanItem.status.in_(OPEN_STATUSES),
            DailyPlanItem.position > item.position,
        )
        .order_by(DailyPlanItem.position)
        .first()
    )
    if nxt is None:
        nxt = (
            db.query(DailyPlanItem)
            .filter(
                DailyPlanItem.user_id == user_id,
                DailyPlanItem.plan_date == item.plan_date,
                DailyPlanItem.status.in_(OPEN_STATUSES),
            )
            .order_by(DailyPlanItem.position)
            .first()
        )
    return _serialize(nxt) if nxt else None


def save_journal(
    db: Session,
    *,
    learned: Optional[str] = None,
    struggled: Optional[str] = None,
    tomorrow: Optional[str] = None,
    user_id: str = DEFAULT_USER,
    timezone_name: Optional[str] = None,
) -> dict[str, Any]:
    entry_date = local_today(timezone_name)
    row = (
        db.query(DayJournal)
        .filter(DayJournal.user_id == user_id, DayJournal.entry_date == entry_date)
        .first()
    )
    if not row:
        row = DayJournal(user_id=user_id, entry_date=entry_date)
        db.add(row)
    if learned is not None:
        row.learned = learned
    if struggled is not None:
        row.struggled = struggled
    if tomorrow is not None:
        row.tomorrow = tomorrow
    row.updated_at = _now()
    db.flush()
    return {
        "entry_date": entry_date,
        "learned": row.learned,
        "struggled": row.struggled,
        "tomorrow": row.tomorrow,
    }
