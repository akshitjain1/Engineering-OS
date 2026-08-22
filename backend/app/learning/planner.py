"""Deterministic daily planner. Fits a minute budget; never skips the curriculum spine.

V3: the planner uses curriculum order, prerequisites, completion state,
unfinished activities, and the manual review queue only. No mastery scores,
diagnostic evidence, confidence, or pace inputs.

Parallel-track aware: manages PRIMARY, SECONDARY, ALWAYS-ON, and PROJECT tracks.
Never schedules a topic before its prerequisites are complete.

Capacity modes:
- weekday: CORE LEARN (+ PRACTICE) + 1 ALWAYS_ON/OPTIONAL parallel + short BUILD if room
- weekend: larger budget; prefer BUILD/PROJECT + deeper PRACTICE + CORE catch-up
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

ITEM_TYPES = (
    "LEARN",
    "PRACTICE",
    "BUILD",
    "REVIEW",
    "ALWAYS_ON",
    "PROJECT",
)

LEARN_MINUTES = 35
PRACTICE_MINUTES = 20
BUILD_MINUTES = 25
REVIEW_MINUTES = 15
ALWAYS_ON_MINUTES = 15
PROJECT_MINUTES = 60
MIN_TAIL_MINUTES = 20

# Track assignments per topic
TRACK_PRIMARY = "P"
TRACK_SECONDARY = "S"
TRACK_ALWAYS_ON = "A"
TRACK_PROJECT = "PJ"

LEARNING_TRACK_TO_CODE = {
    "CORE": TRACK_PRIMARY,
    "SPECIALIZATION": TRACK_SECONDARY,
    "ALWAYS_ON": TRACK_ALWAYS_ON,
    "BUILD": TRACK_PROJECT,
    "OPTIONAL": TRACK_SECONDARY,
}


@dataclass
class TopicView:
    id: int
    slug: str
    name: str
    locked: bool
    lessons_complete: bool
    domain: str
    track: str = TRACK_PRIMARY  # P, S, A, or PJ
    prerequisite_slugs: list[str] = field(default_factory=list)
    unfinished_exercises: int = 0
    practice_pending: int = 0
    project_embedding: bool = False
    parallel_eligible: bool = False
    learning_track: str = "CORE"
    depth_target: str = "WORKING_KNOWLEDGE"
    estimated_minutes: Optional[int] = None
    content_readiness: Optional[str] = None  # READY | NEEDS_REVIEW | ...


@dataclass
class RevisionView:
    id: int
    item_id: int
    item_type: str
    title: str
    topic_slug: Optional[str] = None
    overdue: bool = True


TRACK_ORDER = [TRACK_PRIMARY, TRACK_SECONDARY, TRACK_ALWAYS_ON, TRACK_PROJECT]


def track_code_from_learning_track(learning_track: Optional[str]) -> str:
    if not learning_track:
        return TRACK_PRIMARY
    return LEARNING_TRACK_TO_CODE.get(learning_track.upper(), TRACK_PRIMARY)


def domain_from_slug(slug: str) -> str:
    if slug.startswith("java-"):
        return "java"
    if slug.startswith("dsa-"):
        return "dsa"
    if slug.startswith("se-"):
        return "software-engineering"
    if slug.startswith("db-") or slug.startswith("be-"):
        return "backend"
    if slug.startswith("math-"):
        return "mathematics"
    if slug.startswith("ml-"):
        return "ml"
    return "foundations"


def _cap(minutes: int, remaining: int) -> int:
    return max(0, min(minutes, remaining))


def _item(
    *,
    item_type: str,
    title: str,
    minutes: int,
    why: str,
    topic_id: Optional[int] = None,
    topic_slug: Optional[str] = None,
    domain: Optional[str] = None,
    group: Optional[str] = None,
) -> dict[str, Any]:
    payload = {
        "type": item_type,
        "title": title,
        "minutes": minutes,
        "why": why,
        "topic_id": topic_id,
        "topic_slug": topic_slug,
        "domain": domain,
    }
    if group:
        payload["group"] = group
    return payload


def group_for_item_type(item_type: str) -> str:
    if item_type == "LEARN":
        return "core"
    if item_type == "ALWAYS_ON":
        return "parallel"
    if item_type in {"PRACTICE", "REVIEW"}:
        return "practice"
    if item_type in {"BUILD", "PROJECT"}:
        return "build"
    return "core"


def current_cursor(topics: list[TopicView]) -> Optional[TopicView]:
    """Return the first unlocked CORE/PRIMARY topic with lessons not yet complete.

    Prefer content-READY topics. Avoid RESOURCE_GAP/BROKEN when any other unlocked
    incomplete CORE topic exists. Last resort: first unlocked incomplete CORE.
    """
    ready: Optional[TopicView] = None
    soft: Optional[TopicView] = None
    last_resort: Optional[TopicView] = None
    for topic in topics:
        if topic.track != TRACK_PRIMARY:
            continue
        if topic.locked or topic.lessons_complete:
            continue
        readiness = (topic.content_readiness or "").upper()
        if last_resort is None:
            last_resort = topic
        if readiness == "READY":
            ready = topic
            break
        if readiness in ("RESOURCE_GAP", "BROKEN"):
            continue
        if soft is None:
            soft = topic
    if ready is not None:
        return ready
    if soft is not None:
        return soft
    if last_resort is not None:
        return last_resort
    for topic in topics:
        if topic.track == TRACK_ALWAYS_ON:
            continue
        if topic.locked or topic.lessons_complete:
            continue
        return topic
    return None


def prerequisites_locked(topic: TopicView, all_topics: list[TopicView]) -> bool:
    for prereq_slug in topic.prerequisite_slugs or []:
        prereq = next((t for t in all_topics if t.slug == prereq_slug), None)
        if prereq is None:
            return True
        if prereq.locked:
            return True
        if prereq.prerequisite_slugs and prerequisites_locked(prereq, all_topics):
            return True
    return False


def unlock_status(topic: TopicView, all_topics: list[TopicView]) -> bool:
    if topic.locked:
        return False
    return not prerequisites_locked(topic, all_topics)


def sequential_unlocked(topics: list[TopicView]) -> list[TopicView]:
    return [t for t in topics if not t.locked]


def _track_priority(track: str) -> int:
    try:
        return TRACK_ORDER.index(track)
    except ValueError:
        return len(TRACK_ORDER)


def _track_sort_key(topic: TopicView) -> tuple:
    return (_track_priority(topic.track), topic.id)


def _always_on_items(
    all_topics: list[TopicView], remaining: int, *, max_items: int = 1
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    candidates = [
        t for t in all_topics if t.track == TRACK_ALWAYS_ON and unlock_status(t, all_topics)
    ]
    candidates.sort(key=lambda t: (0 if not t.lessons_complete else 1, t.id))
    for topic in candidates:
        if len(items) >= max_items or remaining <= 0:
            break
        minutes = _cap(ALWAYS_ON_MINUTES, remaining)
        if minutes <= 0:
            break
        items.append(
            _item(
                item_type="ALWAYS_ON",
                title=f"Always-on: {topic.name}",
                minutes=minutes,
                why=f"Foundational engineering skill: {topic.name}. Practice between main blocks.",
                topic_id=topic.id,
                topic_slug=topic.slug,
                domain=topic.domain,
                group="parallel",
            )
        )
        remaining -= minutes
    return items


def _project_items(
    topics: list[TopicView],
    remaining: int,
    *,
    project_hint: Optional[dict[str, Any]] = None,
    prefer_projects: bool = False,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if project_hint and remaining > 0:
        minutes = _cap(int(project_hint.get("minutes") or PROJECT_MINUTES), remaining)
        if minutes > 0:
            items.append(
                _item(
                    item_type="PROJECT",
                    title=f"Build: {project_hint['title']}",
                    minutes=minutes,
                    why=project_hint.get("why")
                    or "Highest-priority available engineering project.",
                    topic_id=project_hint.get("topic_id"),
                    topic_slug=project_hint.get("topic_slug"),
                    domain=project_hint.get("domain") or "build",
                    group="build",
                )
            )
            remaining -= minutes
            if not prefer_projects:
                return items

    for topic in topics:
        if not topic.project_embedding and topic.track != TRACK_PROJECT:
            continue
        if topic.locked or topic.lessons_complete:
            continue
        if remaining <= 0:
            break
        minutes = _cap(PROJECT_MINUTES if prefer_projects else BUILD_MINUTES, remaining)
        if minutes <= 0:
            break
        items.append(
            _item(
                item_type="PROJECT" if prefer_projects else "BUILD",
                title=f"Build: {topic.name}",
                minutes=minutes,
                why="Implementation task for this topic.",
                topic_id=topic.id,
                topic_slug=topic.slug,
                domain=topic.domain,
                group="build",
            )
        )
        remaining -= minutes
        break
    return items


def build_daily_plan(
    *,
    budget_minutes: int,
    topics: list[TopicView],
    overdue_revisions: list[RevisionView],
    goal: str = "Personal learning: focus on primary track today",
    mode: str = "weekday",
    project_hint: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Generate a daily plan respecting prerequisites, tracks, and capacity."""
    empty_groups = {"core": [], "parallel": [], "practice": [], "build": []}
    if budget_minutes <= 0:
        return {
            "budget_minutes": budget_minutes,
            "total_minutes": 0,
            "goal": goal,
            "mode": mode,
            "items": [],
            "groups": empty_groups,
        }

    remaining = budget_minutes
    items: list[dict[str, Any]] = []
    used_slugs: set[str] = set()
    is_weekend = mode == "weekend"

    def add(item: dict[str, Any]) -> bool:
        nonlocal remaining
        minutes = _cap(item["minutes"], remaining)
        if minutes <= 0:
            return False
        group = item.get("group") or group_for_item_type(item["type"])
        payload = {**item, "minutes": minutes, "group": group}
        items.append(payload)
        remaining -= minutes
        if payload.get("topic_slug"):
            used_slugs.add(payload["topic_slug"])
        return True

    for revision in overdue_revisions:
        if remaining <= 0:
            break
        add(
            _item(
                item_type="REVIEW",
                title=f"Revise {revision.title}",
                minutes=REVIEW_MINUTES,
                why="You added this topic to your review queue.",
                topic_id=revision.item_id if revision.item_type == "topic" else None,
                topic_slug=revision.topic_slug,
                group="practice",
            )
        )

    cursor = current_cursor(topics)

    if is_weekend:
        for proj in _project_items(
            topics, remaining, project_hint=project_hint, prefer_projects=True
        ):
            if not add(proj):
                break

        if cursor and cursor.slug not in used_slugs and remaining > 0 and unlock_status(cursor, topics):
            add(
                _item(
                    item_type="LEARN",
                    title=cursor.name,
                    minutes=LEARN_MINUTES,
                    why="Core catch-up on the weekend.",
                    topic_id=cursor.id,
                    topic_slug=cursor.slug,
                    domain=cursor.domain,
                    group="core",
                )
            )
            if cursor.practice_pending and remaining > 0:
                add(
                    _item(
                        item_type="PRACTICE",
                        title=f"Practice {cursor.name}",
                        minutes=min(PRACTICE_MINUTES + 10, remaining),
                        why="Deeper practice block for the weekend.",
                        topic_id=cursor.id,
                        topic_slug=cursor.slug,
                        domain=cursor.domain,
                        group="practice",
                    )
                )
            if cursor.unfinished_exercises and remaining > 0:
                add(
                    _item(
                        item_type="BUILD",
                        title=f"Build: {cursor.name}",
                        minutes=BUILD_MINUTES,
                        why="Finish the implementation task.",
                        topic_id=cursor.id,
                        topic_slug=cursor.slug,
                        domain=cursor.domain,
                        group="build",
                    )
                )

        for item in _always_on_items(topics, remaining, max_items=1):
            if item.get("topic_slug") in used_slugs:
                continue
            if not add(item):
                break
    else:
        if cursor and cursor.slug not in used_slugs and remaining > 0:
            if unlock_status(cursor, topics):
                add(
                    _item(
                        item_type="LEARN",
                        title=cursor.name,
                        minutes=LEARN_MINUTES,
                        why="Next topic in the curriculum sequence.",
                        topic_id=cursor.id,
                        topic_slug=cursor.slug,
                        domain=cursor.domain,
                        group="core",
                    )
                )
                if cursor.practice_pending and remaining > 0:
                    add(
                        _item(
                            item_type="PRACTICE",
                            title=f"Practice {cursor.name}",
                            minutes=PRACTICE_MINUTES,
                            why="Work the mapped practice sources for the current topic.",
                            topic_id=cursor.id,
                            topic_slug=cursor.slug,
                            domain=cursor.domain,
                            group="practice",
                        )
                    )

        for item in _always_on_items(topics, remaining, max_items=1):
            if item.get("topic_slug") in used_slugs:
                continue
            if not add(item):
                break

        if cursor and remaining >= BUILD_MINUTES and cursor.unfinished_exercises:
            add(
                _item(
                    item_type="BUILD",
                    title=f"Build: {cursor.name}",
                    minutes=BUILD_MINUTES,
                    why="Complete the implementation task for the current topic.",
                    topic_id=cursor.id,
                    topic_slug=cursor.slug,
                    domain=cursor.domain,
                    group="build",
                )
            )
        elif remaining >= BUILD_MINUTES and project_hint:
            for proj in _project_items(topics, remaining, project_hint=project_hint):
                if not add(proj):
                    break

        secondary_candidates = sorted(
            [
                t
                for t in topics
                if t.track == TRACK_SECONDARY
                and t.slug not in used_slugs
                and not t.lessons_complete
            ],
            key=_track_sort_key,
        )
        for sec_topic in secondary_candidates:
            if not unlock_status(sec_topic, topics):
                continue
            if remaining < LEARN_MINUTES:
                break
            add(
                _item(
                    item_type="LEARN",
                    title=sec_topic.name,
                    minutes=LEARN_MINUTES,
                    why="Specialization / optional track progress.",
                    topic_id=sec_topic.id,
                    topic_slug=sec_topic.slug,
                    domain=sec_topic.domain,
                    group="parallel",
                )
            )
            break

        if remaining >= MIN_TAIL_MINUTES and cursor:
            follow_candidates = sorted(
                [
                    t
                    for t in sequential_unlocked(topics)
                    if t.slug not in used_slugs
                    and not t.lessons_complete
                    and t.track == TRACK_PRIMARY
                ],
                key=_track_sort_key,
            )
            for follow in follow_candidates:
                if not unlock_status(follow, topics):
                    continue
                add(
                    _item(
                        item_type="LEARN",
                        title=follow.name,
                        minutes=LEARN_MINUTES,
                        why="Next topic after the current one, when time remains.",
                        topic_id=follow.id,
                        topic_slug=follow.slug,
                        domain=follow.domain,
                        group="core",
                    )
                )
                break

    for item in items:
        slug = item.get("topic_slug")
        if not slug:
            continue
        topic = next((t for t in topics if t.slug == slug), None)
        if topic and topic.locked:
            raise RuntimeError(f"planner emitted locked topic {slug}")

    total = sum(item["minutes"] for item in items)
    assert total <= budget_minutes, f"Total {total} exceeds budget {budget_minutes}"

    groups: dict[str, list] = {"core": [], "parallel": [], "practice": [], "build": []}
    for item in items:
        key = item.get("group") or "core"
        groups.setdefault(key, []).append(item)

    return {
        "budget_minutes": budget_minutes,
        "total_minutes": total,
        "goal": goal,
        "mode": mode,
        "cursor_topic_slug": cursor.slug if cursor else None,
        "items": items,
        "groups": groups,
        "track_summary": {
            TRACK_PRIMARY: sum(1 for t in topics if t.track == TRACK_PRIMARY and not t.locked),
            TRACK_SECONDARY: sum(1 for t in topics if t.track == TRACK_SECONDARY and not t.locked),
            TRACK_ALWAYS_ON: sum(1 for t in topics if t.track == TRACK_ALWAYS_ON and not t.locked),
            TRACK_PROJECT: sum(1 for t in topics if t.track == TRACK_PROJECT and not t.locked),
        },
    }
