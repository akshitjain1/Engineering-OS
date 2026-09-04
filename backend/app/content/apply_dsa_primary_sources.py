"""Point each DSA topic at its own page, titled from the page itself.

Every URL is fetched before anything is written. A 404 or a redirect that lands
somewhere else is a hard failure for that entry -- a dead link shipped as a
learner's primary source is worse than the section index it would replace, and
the whole reason these rows were wrong is that somebody wrote titles without
opening the pages.

Titles come from the page's own <title>, cleaned of the site suffix, and are
written in the "GFG - <title>" form the rest of the curriculum already uses.

    python -m app.content.apply_dsa_primary_sources            # dry run
    python -m app.content.apply_dsa_primary_sources --apply
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.content.dsa_primary_sources import DSA_PRIMARY_SOURCES, GFG  # noqa: E402
from app.content.verify_resource_identity import clean_page_title, host_of, page_title  # noqa: E402
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic  # noqa: E402
from app.console import use_utf8  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

CACHE = Path(__file__).parent / "data" / "dsa_primary_source_facts.json"
EM_DASH = "—"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


def load_cache() -> dict[str, Any]:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def fetch(urls: list[str], refresh: bool = False) -> dict[str, Any]:
    facts = {} if refresh else load_cache()
    missing = [u for u in urls if u not in facts]
    if missing:
        print(f"fetching {len(missing)} page(s)...")
        with httpx.Client(follow_redirects=True, timeout=25, headers=_HEADERS) as client:
            for i, url in enumerate(missing, 1):
                entry: dict[str, Any] = {}
                try:
                    resp = client.get(url)
                    entry["status"] = resp.status_code
                    entry["final_url"] = str(resp.url)
                    if resp.status_code == 200:
                        entry["page_title"] = page_title(resp.text)
                except Exception as exc:  # noqa: BLE001
                    entry["error"] = f"{type(exc).__name__}: {exc}"
                facts[url] = entry
                if i % 10 == 0:
                    print(f"  ... {i}/{len(missing)}")
                time.sleep(0.35)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(facts, indent=2, sort_keys=True), encoding="utf-8")
    return facts


def audit(facts: dict[str, Any]) -> list[str]:
    """Every mapping the fetched pages contradict."""
    failures = []
    for slug, (path, why) in sorted(DSA_PRIMARY_SOURCES.items()):
        url = GFG + path
        fact = facts.get(url)
        if not why.strip():
            failures.append(f"{slug}: empty rationale")
        if fact is None:
            failures.append(f"{slug}: never fetched")
            continue
        if fact.get("error"):
            failures.append(f"{slug}: {fact['error']}")
            continue
        if fact.get("status") != 200:
            failures.append(f"{slug}: HTTP {fact.get('status')} for {url}")
            continue
        if host_of(fact.get("final_url", "")) != "geeksforgeeks.org":
            failures.append(f"{slug}: redirected off GeeksforGeeks to {fact.get('final_url')}")
        if not clean_page_title(fact.get("page_title")):
            failures.append(f"{slug}: the page has no usable title")
    return failures


def plan(db, facts: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    for slug, (path, why) in sorted(DSA_PRIMARY_SOURCES.items()):
        url = GFG + path
        title = f"GFG {EM_DASH} {clean_page_title((facts.get(url) or {}).get('page_title'))}"
        row = (
            db.query(CurriculumResource, CurriculumTopic.name)
            .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
            .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
            .filter(CurriculumTopic.slug == slug, CurriculumResource.role == "PRIMARY")
            .first()
        )
        if row is None:
            changes.append({"slug": slug, "missing": True})
            continue
        resource, topic_name = row
        if resource.url == url and resource.title == title and resource.notes == why:
            continue
        changes.append({
            "slug": slug,
            "topic": topic_name,
            "id": resource.id,
            "url_from": resource.url,
            "url_to": url,
            "title_from": resource.title,
            "title_to": title,
            "why": why,
        })
    return changes


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache")
    args = parser.parse_args(argv)

    urls = [GFG + path for path, _ in DSA_PRIMARY_SOURCES.values()]
    facts = fetch(sorted(set(urls)), refresh=args.refresh)

    failures = audit(facts)
    if failures:
        print(f"\n{len(failures)} mapping(s) the pages contradict - nothing written:\n")
        for line in failures:
            print("  FAIL " + line)
        return 1
    print(f"All {len(DSA_PRIMARY_SOURCES)} pages verified against GeeksforGeeks.\n")

    db = SessionLocal()
    try:
        changes = plan(db, facts)
        missing = [c for c in changes if c.get("missing")]
        real = [c for c in changes if not c.get("missing")]
        for c in missing:
            print(f"  SKIP {c['slug']}: no PRIMARY resource on that topic")
        if not real:
            print("Nothing to change - every topic already opens its own page.")
            return 0

        url_changes = [c for c in real if c["url_from"] != c["url_to"]]
        print(f"{len(real)} resource(s) to update, {len(url_changes)} of them a different page:\n")
        for c in real:
            print(f"  {c['topic']}")
            if c["url_from"] != c["url_to"]:
                print(f"      url  : {c['url_from']}")
                print(f"          -> {c['url_to']}")
            print(f"      title: {c['title_from']}")
            print(f"          -> {c['title_to']}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write it.")
            return 0

        for c in real:
            resource = db.get(CurriculumResource, c["id"])
            resource.url = c["url_to"]
            resource.title = c["title_to"]
            resource.provider = "GeeksforGeeks"
            resource.notes = c["why"]
        db.commit()
        print(f"\nUpdated {len(real)} resource(s).")
        print(f"Remaining: {len(plan(db, facts))}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
