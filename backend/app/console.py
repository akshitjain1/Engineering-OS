"""Make stdout able to carry the text we actually print.

Windows gives a redirected Python process the console ANSI code page -- cp1252
here -- and cp1252 cannot encode an em dash, let alone an emoji. Every script
that prints a topic title, a resource title or a line of the journal is one
character away from dying on a `print`, and dying there is worse than it
sounds: the launcher runs these, so the failure lands *before* the work is
saved while the log shows the very lines it was about to save.

That is not hypothetical. A journal entry containing a star (U+2B50) crashed
the study-activity publisher on the first evening it had a full day to publish.
The entries were printed to the log; none of them reached the repository.

Call `use_utf8()` first thing in any script that prints content from the
database.
"""

from __future__ import annotations

import sys


def use_utf8() -> None:
    """Re-encode stdout and stderr as UTF-8, replacing anything that will not fit.

    `errors="replace"` rather than "strict": a character that cannot be shown
    should cost one glyph in a log, never the run.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            # A stream that refuses is not worth failing the run over.
            pass
