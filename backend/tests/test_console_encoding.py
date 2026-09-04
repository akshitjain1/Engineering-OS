"""Printing a day's work must not be able to lose it.

Windows hands a redirected Python process the console ANSI code page -- cp1252
here -- which cannot encode an em dash, let alone an emoji. Every entry the
study-activity publisher builds contains an em dash by construction, and a
journal is written by a human who may well type a star in it.

One did. On the first evening with a full day to publish, `Stuck on — ... ⭐⭐⭐⭐⭐`
raised UnicodeEncodeError on the `print` that lists the entries -- before a
single one reached the repository. The launcher's log showed all seven lines it
was about to save, and saved none of them. A crash while *describing* the work
is the worst place for one, because the log looks like success.

So the encoding is made explicit, and these hold it there.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.console import use_utf8

BACKEND = Path(__file__).resolve().parent.parent
STAR = "⭐"
EM_DASH = "—"


def test_use_utf8_is_safe_to_call_twice():
    """The scripts call it at the top of main; a second call must not throw."""
    use_utf8()
    use_utf8()


def test_use_utf8_survives_a_stream_that_cannot_be_reconfigured(monkeypatch):
    """pytest replaces stdout with objects that have no reconfigure at all."""

    class Dumb:
        pass

    monkeypatch.setattr(sys, "stdout", Dumb())
    monkeypatch.setattr(sys, "stderr", Dumb())
    use_utf8()  # must not raise


def _run(code: str) -> subprocess.CompletedProcess:
    """Run in a child with a cp1252 stdout, the way the launcher does."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        cwd=BACKEND,
        env={"PYTHONIOENCODING": "cp1252", "PATH": "", "SYSTEMROOT": ""},
    )


def test_a_star_in_the_journal_crashes_an_unprotected_print():
    """The failure this exists to prevent, reproduced rather than assumed."""
    result = _run(f'print("Stuck on {EM_DASH} {STAR}")')

    assert result.returncode != 0, "expected cp1252 to reject the star"
    assert b"UnicodeEncodeError" in result.stderr


def test_use_utf8_lets_the_same_line_through():
    result = _run(
        "import sys; sys.path.insert(0, '.');"
        "from app.console import use_utf8; use_utf8();"
        f'print("Stuck on {EM_DASH} {STAR}")'
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert STAR.encode("utf-8") in result.stdout
    assert EM_DASH.encode("utf-8") in result.stdout


def test_the_publisher_calls_it_before_printing_anything():
    """Ordering is the whole point: the guard must precede the first print."""
    text = (BACKEND / "scripts" / "publish_study_activity.py").read_text(encoding="utf-8")
    body = text.split("def main(", 1)[1]

    assert "use_utf8()" in body, "the publisher no longer protects its output"
    assert body.index("use_utf8()") < body.index("print("), (
        "use_utf8() must run before the first print, or the guard is decorative"
    )
