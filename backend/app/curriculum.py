"""Deterministic curriculum status, progress, and prerequisite evaluation."""

from __future__ import annotations

from typing import Any, Iterable, Optional

COMPLETED_LESSON_STATES = frozenset({"completed", "mastered", "fast_tracked"})
IN_PROGRESS_LESSON_STATES = frozenset({"in_progress", "learning", "practicing", "needs_revision"})
NOT_STARTED_STATES = frozenset({"not_started", ""})

UI_LESSON_STATES = frozenset({"not_started", "in_progress", "completed"})

STATE_ALIASES = {
    "completed": "completed",
    "in_progress": "in_progress",
    "not_started": "not_started",
    "learning": "in_progress",
    "practicing": "in_progress",
    "needs_revision": "in_progress",
    "mastered": "completed",
    "fast_tracked": "completed",
}


def normalize_lesson_state(state: str) -> str:
    return STATE_ALIASES.get((state or "").strip().lower(), (state or "").strip().lower())


def is_lesson_complete(status: str | None) -> bool:
    return normalize_lesson_state(status or "not_started") == "completed"


def lesson_ui_status(status_or_lock: Any, progress: Any = None) -> Any:
    """Unified lesson UI status — accepts every historical call signature safely.

    Contract 1 (string): lesson_ui_status("completed") -> "completed"
        Normalizes DB states via STATE_ALIASES into UI_LESSON_STATES.
    Contract 2 (lock dict, optional progress dict):
        lesson_ui_status({"locked": True, "items": [...], "total": n}) ->
            {"locked", "progress_percent", "message"}
    """
    # Legacy planner-lock form (two args, first a dict)
    if isinstance(status_or_lock, dict):
        lock = status_or_lock
        percent = module_progress(lock.get("items", []), int(lock.get("total", 0) or 0)).get(
            "percentage", 0
        )
        return {
            "locked": bool(lock.get("locked", False)),
            "progress_percent": percent,
            "message": lock.get("message"),
        }
    # String completion-status form
    normalized = normalize_lesson_state(status_or_lock or "not_started")
    if normalized in UI_LESSON_STATES:
        return normalized
    return "not_started"


def ratio(completed: int, total: int) -> dict[str, Any]:
    percent = round((completed / total) * 100) if total else 0
    return {"completed": completed, "total": total, "percent": percent}


def topic_lesson_progress(lessons: Iterable[Any]) -> dict[str, Any]:
    lesson_list = list(lessons)
    completed = sum(1 for lesson in lesson_list if is_lesson_complete(getattr(lesson, "completion_status", None)))
    in_progress = sum(
        1 for lesson in lesson_list if lesson_ui_status(getattr(lesson, "completion_status", None)) == "in_progress"
    )
    progress = ratio(completed, len(lesson_list))
    if not lesson_list:
        ui_status = "not_started"
    elif completed == len(lesson_list):
        ui_status = "completed"
    elif completed or in_progress:
        ui_status = "in_progress"
    else:
        ui_status = "not_started"
    return {**progress, "status": ui_status}


def is_topic_complete(lessons: Iterable[Any]) -> bool:
    lesson_list = list(lessons)
    if not lesson_list:
        return False
    return all(is_lesson_complete(getattr(lesson, "completion_status", None)) for lesson in lesson_list)


def _prereq_complete(topic: Any, completion_lookup: dict[str, bool] | None) -> bool:
    if completion_lookup is not None:
        slug = getattr(topic, "slug", None)
        if slug and slug in completion_lookup:
            return completion_lookup[slug]
        name = getattr(topic, "name", None)
        if name and name in completion_lookup:
            return completion_lookup[name]
    return is_topic_complete(getattr(topic, "lessons", []) or [])


def _extract_slug_from_ref(ref: Any) -> str:
    """Extract the slug from a prerequisite reference.

    Supports two formats:
    - String: the slug itself (backward compatible)
    - Dict with 'slug' key: extract the slug
    """
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        return ref.get("slug", str(ref))
    return str(ref)


def evaluate_prerequisites(
    prerequisite_refs: list[str] | None,
    topics_index: dict[str, Any],
    completion_lookup: dict[str, bool] | None = None,
) -> dict[str, Any]:
    refs = [ref for ref in (prerequisite_refs or []) if ref]
    items = []
    missing = []
    for ref in refs:
        slug = _extract_slug_from_ref(ref)
        topic = topics_index.get(slug)
        if topic is None:
            complete = False
            found = False
            display = ref
        else:
            complete = _prereq_complete(topic, completion_lookup)
            found = True
            display = getattr(topic, 'name', None) or slug
        items.append({'name': display, 'slug': slug, 'complete': complete, 'found': found})
        if not complete:
            missing.append(display)

    locked = bool(missing)
    if not refs:
        message = None
    elif locked:
        if len(missing) == 1:
            message = f'Complete {missing[0]} to unlock this topic.'
        else:
            message = 'Complete these topics to unlock: ' + ', '.join(missing) + '.'
    else:
        message = None

    return {'locked': locked, 'message': message, 'items': items, 'missing': missing}

def compose_topic_status(locked: bool, lesson_progress: dict[str, Any]) -> str:
    if locked:
        return 'locked'
    # HEAD contract: trust topic_lesson_progress tri-state (not_started /
    # in_progress / completed) instead of a percentage heuristic.
    return lesson_progress.get('status', 'not_started')


def module_progress(items: list[dict[str, Any]], total: Optional[int] = None) -> dict[str, Any]:
    """Dual-signature compatibility.

    Legacy single-arg: module_progress(topic_nodes) — counts nodes with
    status == "completed" and returns ratio().
    Two-arg form: module_progress(items, total) — counts truthy 'complete'.
    """
    if total is None:
        complete = sum(1 for topic in items if topic.get("status") == "completed")
        return ratio(complete, len(items))
    completed = sum(1 for i in items if i.get('complete', False))
    return {"completed": completed, "total": total, "percentage": round(completed / total * 100, 1) if total > 0 else 0}


def subject_progress(items: list[dict[str, Any]], total: Optional[int] = None) -> dict[str, Any]:
    """Dual-signature compatibility (mirrors module_progress)."""
    if total is None:
        complete = sum(
            1
            for module in items
            if module.get("progress", {}).get("total")
            and module["progress"]["completed"] == module["progress"]["total"]
        )
        return ratio(complete, len(items))
    completed = sum(1 for i in items if i.get('complete', False))
    return {'completed': completed, 'total': total, 'percentage': round(completed / total * 100, 1) if total > 0 else 0}
