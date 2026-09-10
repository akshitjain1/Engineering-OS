"""Point each foundations topic at its own page, verifying every one first.

Nothing here is trusted from the map. Each URL is fetched, and it is written
only if:

  * it answers 200,
  * it does not redirect to another host,
  * it yields a real <title>, and
  * audit_topic_relevance says the topic's name is in that title or the <h1>.

The last condition is the point. The previous round of this work wrote 44 DSA
sources that were all reachable, all correctly titled, and 3 of which were
still the wrong page -- because "does it load" and "is it about this" are
different questions. The gate here is the same code that does the auditing, so
a source cannot be written that the audit would immediately flag.

The page being replaced is demoted to REFERENCE, not deleted. MIT's shell
lecture is good material; it was simply doing the work of fourteen pages.

    python -m app.content.apply_foundations_primary_sources          # dry run
    python -m app.content.apply_foundations_primary_sources --apply
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.console import use_utf8  # noqa: E402
from app.content import audit_topic_relevance as audit  # noqa: E402
from app.content.foundations_primary_sources import SOURCES  # noqa: E402
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

#: Where a demoted PRIMARY goes. It stays visible and stays openable; it just
#: stops being the thing the day tells you to read.
DEMOTED_ROLE = "REFERENCE"

PROVIDERS = {
    "geeksforgeeks.org": "GeeksforGeeks",
    "en.wikipedia.org": "Wikipedia",
    "ubuntu.com": "Ubuntu",
    "web.stanford.edu": "Stanford CS101",
}


def provider_for(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    return PROVIDERS.get(host, host)


def clean_title(raw: str) -> str:
    """The page's own title, minus the site's advertising."""
    text = " ".join(raw.split())
    for sep in (" - GeeksforGeeks", " | GeeksforGeeks", " - Wikipedia",
                " | Ubuntu", " · Prettier"):
        if text.endswith(sep):
            text = text[: -len(sep)]
    return text.strip(" -|·")


def verify(client: httpx.Client, url: str, name: str, slug: str) -> tuple[str | None, str]:
    """(title, reason). A title means it passed; otherwise reason says why not."""
    try:
        resp = client.get(url)
        if resp.status_code == 403:
            retry = client.get(url, headers=audit._POLITE_HEADERS)
            if retry.status_code == 200:
                resp = retry
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"

    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"

    landed = urlsplit(str(resp.url)).hostname or ""
    wanted = urlsplit(url).hostname or ""
    if landed.removeprefix("www.") != wanted.removeprefix("www."):
        return None, f"redirected off-host to {landed}"

    entry = audit.extract(resp.text)
    if audit.looks_blocked(entry):
        return None, "served a challenge or an empty shell"
    if not entry["title"]:
        return None, "no <title>"

    phrase = audit.topic_phrase(name, slug)
    where = audit.placement(entry, phrase)
    if where != audit.SUBJECT:
        return None, (f"{where}: '{entry['title']}' does not name "
                      f"{' '.join(phrase)!r} in its title or h1")
    return clean_title(entry["title"]), "ok"


def primary_of(db, slug: str):
    return (
        db.query(CurriculumResource)
        .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
        .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
        .filter(CurriculumTopic.slug == slug,
                CurriculumResource.role == "PRIMARY")
        .order_by(CurriculumResource.order_index)
        .first()
    )


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write to the database")
    parser.add_argument("--only", help="one slug, for re-checking a single fix")
    args = parser.parse_args(argv)

    wanted = {args.only: SOURCES[args.only]} if args.only else SOURCES

    db = SessionLocal()
    try:
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        passed: list[tuple[str, str, str, str]] = []   # slug, url, title, old_url
        failed: list[tuple[str, str, str]] = []        # slug, url, reason

        with httpx.Client(follow_redirects=True, timeout=30, headers=audit._HEADERS) as client:
            for slug, (url, _why) in wanted.items():
                topic = topics.get(slug)
                if topic is None:
                    failed.append((slug, url, "no such topic"))
                    continue
                title, reason = verify(client, url, topic.name, slug)
                current = primary_of(db, slug)
                if title is None:
                    failed.append((slug, url, reason))
                    print(f"REJECT  {topic.name[:26]:<26} {reason[:78]}")
                else:
                    old = current.url if current else "(none)"
                    passed.append((slug, url, title, old))
                    print(f"ok      {topic.name[:26]:<26} {title[:52]}")
                time.sleep(0.3)

        print(f"\n{len(passed)} verified, {len(failed)} rejected")
        if failed:
            print("\nRejected -- these keep the page they have:")
            for slug, url, reason in failed:
                print(f"  {slug:<32} {reason}")
                print(f"      {url}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write.")
            return 0

        written = 0
        for slug, url, title, _old in passed:
            topic = topics[slug]
            current = primary_of(db, slug)
            if current is None:
                print(f"  !! {slug} has no PRIMARY row to update; skipped")
                continue
            if current.url == url:
                continue
            # Keep the old material, demoted. It is not wrong -- MIT's shell
            # lecture is good -- it was doing the work of fourteen pages.
            already = (
                db.query(CurriculumResource)
                .filter(CurriculumResource.lesson_id == current.lesson_id,
                        CurriculumResource.url == current.url,
                        CurriculumResource.role == DEMOTED_ROLE)
                .first()
            )
            if already is None:
                db.add(CurriculumResource(
                    slug=f"{current.slug}-ref",
                    title=current.title,
                    url=current.url,
                    resource_type=current.resource_type,
                    lesson_id=current.lesson_id,
                    role=DEMOTED_ROLE,
                    order_index=(current.order_index or 0) + 50,
                    learner_visible=True,
                    provider=getattr(current, "provider", None),
                    notes="Kept as background: this was the topic's primary "
                          "source before it got a page of its own.",
                ))

            current.url = url
            current.title = title
            current.provider = provider_for(url)
            current.notes = SOURCES[slug][1]
            # completion_status is deliberately left alone. Resetting it would
            # be defensible -- the new page is unread -- but it would resurrect
            # finished work as unfinished, and a planner that re-opens days you
            # already closed is worse than one pointing at a page you skimmed.
            written += 1
            print(f"  {topic.name[:26]:<26} -> {title[:44]}")

        db.commit()
        print(f"\n{written} primary source(s) rewritten.")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
