"""Add verified resources to existing topics.

The repair tooling next door fixes URLs that are wrong. This adds ones that
were missing: a topic whose mapped page is correct but incomplete, where a
second source genuinely closes the gap.

Additions are idempotent, keyed on (topic slug, URL), and every URL is fetched
and confirmed before it is written. A resource is added as SUPPLEMENT or
REFERENCE rather than PRIMARY unless stated, so the topic's main study path
does not change under the learner's feet.

Run:
    python -m app.content.add_resources --dry-run
    python -m app.content.add_resources
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from concurrent.futures import ThreadPoolExecutor

from .audit_resource_links import fetch

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"


@dataclass(frozen=True)
class Addition:
    topic_slug: str
    title: str
    url: str
    provider: str
    resource_type: str
    role: str
    estimated_minutes: int
    #: Why this page earns a place next to the one already mapped.
    why: str
    section: str = "FULL_SINGLE_PAGE"
    difficulty: Optional[str] = None
    exactness: str = "EXACT"


#: `uv` is the Astral Python package manager. It belongs here for a specific
#: reason rather than novelty: the environment and dependency topics teach venv
#: and pip, and a learner who has only seen those does not know what a resolver
#: or a lockfile buys them. uv makes that concrete, and it is what these topics'
#: material would look like if written today.
ADDITIONS: tuple[Addition, ...] = (
    Addition(
        topic_slug="cf-dependency-management",
        title="uv - locking and syncing dependencies",
        url="https://docs.astral.sh/uv/concepts/projects/sync/",
        provider="Astral",
        resource_type="documentation",
        role="SUPPLEMENT",
        estimated_minutes=12,
        why=(
            "The mapped guide explains pinning with pip and a requirements file. This shows the "
            "same job with a resolver and a lockfile, which is what makes an install reproducible "
            "rather than merely repeatable."
        ),
    ),
    Addition(
        topic_slug="cf-dev-package-manager",
        title="uv - the pip interface, and what it replaces",
        url="https://docs.astral.sh/uv/pip/",
        provider="Astral",
        resource_type="documentation",
        role="SUPPLEMENT",
        estimated_minutes=10,
        why=(
            "Maps uv's commands onto the pip commands the topic already teaches, so the tool is "
            "learnable from what you know rather than as a separate subject."
        ),
    ),
    Addition(
        topic_slug="py-syntax",
        title="uv - working on projects",
        url="https://docs.astral.sh/uv/guides/projects/",
        provider="Astral",
        resource_type="documentation",
        role="SUPPLEMENT",
        estimated_minutes=12,
        why=(
            "Shows the modern shape of a Python project: pyproject.toml, a managed virtual "
            "environment and a lockfile, instead of a hand-rolled venv plus a requirements file."
        ),
    ),
    # The topic's objective says "compute mean and variance", but the mapped
    # OpenStax section 2.5 is Measures of the Center: mean, median and mode
    # only. Variance and standard deviation are section 2.7, so the objective
    # was unreachable from the mapped page.
    Addition(
        topic_slug="math-stats-summary",
        title="OpenStax - 2.7 Measures of the Spread of the Data",
        url="https://openstax.org/books/introductory-statistics-2e/pages/2-7-measures-of-the-spread-of-the-data",
        provider="OpenStax",
        resource_type="book",
        role="SUPPLEMENT",
        estimated_minutes=25,
        why=(
            "The mapped section covers only mean, median and mode. Variance and standard "
            "deviation, which this topic's objective names, are taught here."
        ),
        section="Measures of the spread of the data",
    ),
)


def collect(conn: sqlite3.Connection) -> tuple[list[dict], list[str]]:
    conn.row_factory = sqlite3.Row
    planned: list[dict] = []
    skipped: list[str] = []

    for addition in ADDITIONS:
        topic = conn.execute(
            "SELECT id, name FROM curriculum_topics WHERE slug = ?", (addition.topic_slug,)
        ).fetchone()
        if topic is None:
            skipped.append(f"topic {addition.topic_slug!r} does not exist")
            continue

        lesson = conn.execute(
            "SELECT id FROM curriculum_lessons WHERE topic_id = ? ORDER BY order_index LIMIT 1",
            (topic["id"],),
        ).fetchone()
        if lesson is None:
            skipped.append(f"topic {addition.topic_slug!r} has no lesson to attach a resource to")
            continue

        existing = conn.execute(
            """
            SELECT r.id FROM curriculum_resources r
              JOIN curriculum_lessons l ON r.lesson_id = l.id
             WHERE l.topic_id = ? AND r.url = ?
            """,
            (topic["id"], addition.url),
        ).fetchone()
        if existing is not None:
            skipped.append(f"{addition.topic_slug}: already has {addition.url}")
            continue

        next_order = conn.execute(
            """
            SELECT COALESCE(MAX(r.order_index), -1) + 1 FROM curriculum_resources r
              JOIN curriculum_lessons l ON r.lesson_id = l.id
             WHERE l.topic_id = ?
            """,
            (topic["id"],),
        ).fetchone()[0]

        planned.append(
            {
                "addition": addition,
                "lesson_id": lesson["id"],
                "topic_name": topic["name"],
                "order_index": next_order,
            }
        )

    return planned, skipped


def verify(planned: list[dict], workers: int = 8) -> tuple[list[dict], list[dict]]:
    urls = sorted({p["addition"].url for p in planned})
    if not urls:
        return [], []
    print(f"verifying {len(urls)} URL(s) before adding...")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = {c.url: c for c in pool.map(fetch, urls)}

    good, bad = [], []
    for plan in planned:
        check = checks[plan["addition"].url]
        landed = (check.final_url or "").rstrip("/")
        drifted = bool(landed) and landed != plan["addition"].url.rstrip("/")
        plan["page_title"] = check.page_title
        plan["http_status"] = check.status
        if check.status in (200, 403) and not drifted:
            good.append(plan)
        else:
            plan["error"] = check.error or f"redirected to {check.final_url}"
            bad.append(plan)
    return good, bad


def apply(conn: sqlite3.Connection, planned: list[dict]) -> int:
    stamped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for plan in planned:
        addition: Addition = plan["addition"]
        conn.execute(
            """
            INSERT INTO curriculum_resources (
                title, url, resource_type, provider, topic, duration, difficulty,
                description, official_unofficial, order_index, completion_status,
                lesson_id, role, section, verification_status, estimated_minutes,
                exactness, notes, estimate_confidence, estimate_method,
                verification_evidence, last_verified_at, learner_visible
            ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 'official', ?, 'not_started',
                      ?, ?, ?, 'NEEDS_REVIEW', ?, ?, ?, 'MEDIUM', 'AUTHORED_ESTIMATE',
                      ?, ?, 1)
            """,
            (
                addition.title,
                addition.url,
                addition.resource_type,
                addition.provider,
                plan["topic_name"],
                addition.difficulty,
                addition.why,
                plan["order_index"],
                plan["lesson_id"],
                addition.role,
                addition.section,
                addition.estimated_minutes,
                addition.exactness,
                addition.why,
                json.dumps(
                    {
                        "link_check": {
                            "checked_at": stamped_at,
                            "http_status": plan.get("http_status"),
                            "page_title": plan.get("page_title"),
                            "note": "URL liveness and page identity only; not concept coverage",
                        }
                    }
                ),
                stamped_at,
            ),
        )
    conn.commit()
    return len(planned)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    planned, skipped = collect(conn)
    for note in skipped:
        print(f"  - skipped: {note}")

    if not planned:
        print("nothing to add")
        return

    good, bad = verify(planned)
    print(f"\n{len(good)} resource(s) ready to add:")
    for plan in good:
        addition = plan["addition"]
        print(f"  [{addition.topic_slug}] {addition.role} {addition.provider} - {addition.title}")
        print(f"      {addition.url}  (HTTP {plan['http_status']}, {plan.get('page_title')})")
    for plan in bad:
        print(f"  ! rejected {plan['addition'].url}: {plan['error']}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "resource_additions.json").write_text(
        json.dumps(
            {
                "added": [] if args.dry_run else [p["addition"].url for p in good],
                "planned": [p["addition"].url for p in good],
                "rejected": [p["addition"].url for p in bad],
                "skipped": skipped,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return
    print(f"\nadded {apply(conn, good)} resource(s)")


if __name__ == "__main__":
    main()
