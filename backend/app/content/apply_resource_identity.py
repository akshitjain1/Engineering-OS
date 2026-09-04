"""Correct resource providers and titles that describe a different page.

Reads the proposals from `verify_resource_identity.corrections` and writes them.
Dry-runs by default, because this rewrites learner-facing text on rows the
learner is about to see.

    python -m app.content.apply_resource_identity            # dry run
    python -m app.content.apply_resource_identity --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.content.verify_resource_identity import (  # noqa: E402
    corrections,
    fetch_titles,
    load_cache,
    rows,
)
from app.db.models import CurriculumResource  # noqa: E402
from app.console import use_utf8  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="fetch page titles that are not cached (needs network)",
    )
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        facts = load_cache()
        if args.refetch:
            urls = [r.url for r, _ in rows(db)]
            facts = fetch_titles(urls)
        proposed = corrections(db, facts)

        if not proposed:
            print("Nothing to correct - every provider matches the host it points at.")
            return 0

        retitled = [c for c in proposed if c["title_to"]]
        print(f"{len(proposed)} provider(s) to correct, {len(retitled)} title(s) to rebuild\n")
        for change in sorted(proposed, key=lambda c: c["id"]):
            print(f"  id {change['id']:<5} [{change['topic']}]")
            print(f"        provider: {change['provider_from']} -> {change['provider_to']}")
            if change["title_to"]:
                print(f"        title   : {change['title_from']}")
                print(f"               -> {change['title_to']}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write it.")
            return 0

        for change in proposed:
            resource = db.get(CurriculumResource, change["id"])
            if resource is None:
                continue
            resource.provider = change["provider_to"]
            if change["title_to"]:
                resource.title = change["title_to"]
        db.commit()
        print(f"\nUpdated {len(proposed)} resource(s).")

        left = corrections(db, facts)
        print(f"Remaining mismatches: {len(left)}")
        return 0 if not left else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
