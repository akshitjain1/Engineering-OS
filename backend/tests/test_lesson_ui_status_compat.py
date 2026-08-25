"""PART A.1 — lesson_ui_status compatibility tests.

Covers every historical call pattern across the codebase:
1. app.curriculum.lesson_ui_status(string)            (topic_lesson_progress, main.py)
2. app.content.resources.lesson_ui_status(string)     (serialize_resource via re-export delegate)
3. app.curriculum.lesson_ui_status(lock_dict)         (legacy two-arg planner-lock form)
4. app.curriculum.lesson_ui_status(lock_dict, progress) (explicit two-arg form)
5. normalize_lesson_state alias behavior (mastered -> completed etc.)
6. is_lesson_complete across all DB states
"""
import pytest

from app.curriculum import (
    is_lesson_complete,
    lesson_ui_status,
    normalize_lesson_state,
    topic_lesson_progress,
)


class TestStringContract:
    def test_completed(self):
        assert lesson_ui_status("completed") == "completed"

    def test_mastered_maps_to_completed(self):
        assert lesson_ui_status("mastered") == "completed"

    def test_fast_tracked_maps_to_completed(self):
        assert lesson_ui_status("fast_tracked") == "completed"

    def test_in_progress_states(self):
        for s in ("in_progress", "learning", "practicing", "needs_revision"):
            assert lesson_ui_status(s) == "in_progress", s

    def test_not_started_and_empty(self):
        assert lesson_ui_status("not_started") == "not_started"
        assert lesson_ui_status("") == "not_started"
        assert lesson_ui_status(None) == "not_started"

    def test_unknown_state_falls_back(self):
        assert lesson_ui_status("weird-state") == "not_started"


class TestLegacyLockDictContract:
    def test_lock_dict_locked(self):
        result = lesson_ui_status({"locked": True, "items": [], "total": 0})
        assert result["locked"] is True
        assert "progress_percent" in result
        assert "message" in result

    def test_lock_dict_unlocked_with_progress(self):
        lock = {
            "locked": False,
            "message": None,
            "items": [{"complete": True}, {"complete": True}, {"complete": False}],
            "total": 3,
        }
        result = lesson_ui_status(lock, {"completed": 2, "total": 3})
        assert result["locked"] is False
        assert result["progress_percent"] == pytest.approx(66.7, abs=0.1)

    def test_resources_module_delegate_matches_canonical_string_form(self):
        from app.content.resources import lesson_ui_status as resources_version

        for state in ("completed", "not_started", "learning", "mastered", None):
            assert resources_version(state) == lesson_ui_status(state), state

    def test_resources_module_delegate_matches_canonical_lock_form(self):
        from app.content.resources import lesson_ui_status as resources_version

        lock = {"locked": True, "items": [], "total": 0}
        assert resources_version(lock) == lesson_ui_status(lock)


class TestNormalizeAliases:
    def test_aliases(self):
        assert normalize_lesson_state("mastered") == "completed"
        assert normalize_lesson_state("fast_tracked") == "completed"
        assert normalize_lesson_state("learning") == "in_progress"
        assert normalize_lesson_state("practicing") == "in_progress"
        assert normalize_lesson_state("needs_revision") == "in_progress"
        assert normalize_lesson_state("completed") == "completed"
        assert normalize_lesson_state("in_progress") == "in_progress"
        assert normalize_lesson_state("not_started") == "not_started"
        # Canonical behavior: None normalizes to "" (callers guard with `or "not_started"`)
        assert normalize_lesson_state(None) == ""

    def test_is_lesson_complete_all_db_states(self):
        complete_states = ("completed", "mastered", "fast_tracked")
        incomplete = ("not_started", "", None, "learning", "practicing", "needs_revision")
        for s in complete_states:
            assert is_lesson_complete(s) is True, s
        for s in incomplete:
            assert is_lesson_complete(s) is False, s


class TestTopicLessonProgress:
    class _L:
        def __init__(self, status):
            self.completion_status = status

    def test_mixed_lessons(self):
        lessons = [self._L("completed"), self._L("learning"), self._L("not_started")]
        out = topic_lesson_progress(lessons)
        assert out["completed"] == 1
        assert out["total"] == 3
        assert out["status"] == "in_progress"

    def test_empty(self):
        assert topic_lesson_progress([])["status"] == "not_started"

    def test_all_mastered(self):
        lessons = [self._L("mastered"), self._L("fast_tracked")]
        assert topic_lesson_progress(lessons)["status"] == "completed"
