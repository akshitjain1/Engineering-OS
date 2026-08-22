"""Deterministic curriculum status, progress, and prerequisite evaluation."""

from __future__ import annotations

from typing import Any, Iterable

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


def lesson_ui_status(status: str | None) -> str:
    normalized = normalize_lesson_state(status or "not_started")
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


def evaluate_prerequisites(
    prerequisite_refs: list[str] | None,
    topics_index: dict[str, Any],
    completion_lookup: dict[str, bool] | None = None,
) -> dict[str, Any]:
    refs = [ref for ref in (prerequisite_refs or []) if ref]
    items = []
    missing = []
    for ref in refs:
        topic = topics_index.get(ref)
        if topic is None:
            complete = False
            found = False
            display = ref
        else:
            complete = _prereq_complete(topic, completion_lookup)
            found = True
            display = getattr(topic, "name", None) or ref
        items.append({"name": display, "slug": ref, "complete": complete, "found": found})
        if not complete:
            missing.append(display)

    locked = bool(missing)
    if not refs:
        message = None
    elif locked:
        if len(missing) == 1:
            message = f"Complete {missing[0]} to unlock this topic."
        else:
            message = "Complete these topics to unlock: " + ", ".join(missing) + "."
    else:
        message = None

    return {
        "locked": locked,
        "items": items,
        "missing": missing,
        "message": message,
    }


def compose_topic_status(locked: bool, lesson_progress: dict[str, Any]) -> str:
    if locked:
        return "locked"
    return lesson_progress["status"]


def module_progress(topics: list[dict[str, Any]]) -> dict[str, Any]:
    complete = sum(1 for topic in topics if topic.get("status") == "completed")
    return ratio(complete, len(topics))


def subject_progress(modules: list[dict[str, Any]]) -> dict[str, Any]:
    complete = sum(1 for module in modules if module["progress"]["total"] and module["progress"]["completed"] == module["progress"]["total"])
    return ratio(complete, len(modules))
