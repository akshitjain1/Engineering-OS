"""Push corrected content back into the manifests, so repairs survive re-import.

## The trap this closes

Curriculum manifests under ``content/curriculum/`` are the source of truth for
every topic they define. ``import_curriculum`` upserts them into the database,
overwriting whatever is there.

So a repair applied only to ``dev.db`` is temporary. Running the index import
after a repair session silently reverted:

- 16 resource URLs, back to a LangChain course catalogue for RAG, back to
  FastAPI's hello-world page for model serving, back to the tutorial table of
  contents for Python tooling
- 142 section boundaries, back to strings that echoed the URL
- **all 94 template-filler questions**, because the manifests still carried
  ``Core idea of {TOPIC}?`` with "A vague buzzword" as a distractor

That last one is the important one. It is not a bug in the repair tooling; it
is what happens when two files claim the same field. 106 topics had questions
defined in *both* a manifest and an authored bank, and whichever import ran
last won.

## What this script does

**Resources.** Copies ``url``, ``title``, ``provider``, ``role`` and ``section``
from the database into the matching manifest entry, matched on resource slug.
The database is the repaired truth after an audit-and-repair pass; this makes
the manifests agree with it.

**Questions.** Deletes the ``questions:`` block from any manifest lesson whose
topic has an authored bank in ``content/questions/``. Question ownership moves
to the bank, permanently and in one place.

Manifest questions for topics with *no* bank keep living in the manifest --
those are the hand-written Domain 0, Java and DSA questions, and they are the
real content until someone migrates them. For those, the question text is
synced from the database instead, matched on question slug, so a targeted
rewrite survives. That is what `repair_question_prompts.py` does to the ten
questions whose prompt said nothing without the page around it (`Stable?`,
`Common bug?`), and without this sync the manifest would put the terse version
straight back.

Nothing else in a manifest is touched: structure, prerequisites, objectives,
mastery criteria and lesson descriptions are left exactly as authored.

Run:
    python -m app.content.sync_manifests --dry-run
    python -m app.content.sync_manifests
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path

import yaml

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
CURRICULUM = BACKEND / "content" / "curriculum"
QUESTIONS = BACKEND / "content" / "questions"
REPORTS = BACKEND / "reports"

#: Fields this script is allowed to change on a resource. Deliberately narrow:
#: exactly the ones the audit and repair tooling writes.
RESOURCE_FIELDS = ("url", "title", "provider", "role", "section")

#: Question fields synced back for manifest-owned questions. Same principle:
#: only what the repair tooling writes.
QUESTION_FIELDS = ("prompt", "options", "answer", "explanation", "difficulty")


def manifest_files() -> list[Path]:
    return [
        p
        for p in sorted(CURRICULUM.rglob("*.yaml"))
        if p.name != "v1-index.yaml" and "_examples" not in p.parts
    ]


def banked_topics() -> set[str]:
    """Topic slugs whose questions are owned by a file in content/questions/."""
    owned: set[str] = set()
    if not QUESTIONS.exists():
        return owned
    for path in sorted(QUESTIONS.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for entry in data.get("topics") or []:
            slug = (entry or {}).get("topic")
            if slug:
                owned.add(slug)
    return owned


def db_questions(conn: sqlite3.Connection) -> dict[str, dict]:
    """Question slug -> the stored content, shaped like a manifest entry."""
    conn.row_factory = sqlite3.Row
    out: dict[str, dict] = {}
    for row in conn.execute(
        "SELECT slug, question, options, answer, explanation, difficulty "
        "FROM lesson_questions WHERE slug IS NOT NULL AND slug != ''"
    ):
        try:
            options = json.loads(row["options"] or "[]")
        except (TypeError, ValueError):
            options = []
        out[row["slug"]] = {
            "prompt": row["question"],
            "options": options if isinstance(options, list) else [],
            "answer": row["answer"],
            "explanation": row["explanation"],
            "difficulty": row["difficulty"],
        }
    return out


def db_resources(conn: sqlite3.Connection) -> dict[str, dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT slug, url, title, provider, role, section FROM curriculum_resources "
        "WHERE slug IS NOT NULL AND slug != ''"
    )
    return {row["slug"]: dict(row) for row in rows}


def sync(dry_run: bool = False) -> dict:
    conn = sqlite3.connect(DB_PATH)
    live = db_resources(conn)
    live_questions = db_questions(conn)
    owned = banked_topics()

    changes: list[dict] = []
    question_edits: list[dict] = []
    stripped: list[dict] = []
    touched_files: Counter[str] = Counter()

    for path in manifest_files():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if data.get("kind") != "curriculum_manifest":
            continue
        rel = str(path.relative_to(BACKEND)).replace("\\", "/")
        dirty = False

        for level in data.get("track", {}).get("levels") or []:
            for subject in level.get("subjects") or []:
                for module in subject.get("modules") or []:
                    for topic in module.get("topics") or []:
                        topic_slug = topic.get("slug")
                        for lesson in topic.get("lessons") or []:
                            # --- questions: the bank owns them if one exists ---
                            existing = lesson.get("questions") or []
                            if existing and topic_slug in owned:
                                stripped.append(
                                    {
                                        "file": rel,
                                        "topic": topic_slug,
                                        "lesson": lesson.get("slug"),
                                        "removed": len(existing),
                                    }
                                )
                                lesson["questions"] = []
                                dirty = True
                                touched_files[rel] += 1
                            elif existing:
                                # No bank owns this topic, so the manifest keeps
                                # its questions -- but a targeted rewrite in the
                                # database has to survive the next import.
                                for question in existing:
                                    slug = question.get("slug")
                                    stored = live_questions.get(slug)
                                    if not slug or stored is None:
                                        continue
                                    for field in QUESTION_FIELDS:
                                        new = stored.get(field)
                                        if new in (None, "") or new == question.get(field):
                                            continue
                                        question_edits.append(
                                            {
                                                "file": rel,
                                                "topic": topic_slug,
                                                "question": slug,
                                                "field": field,
                                            }
                                        )
                                        question[field] = new
                                        dirty = True
                                        touched_files[rel] += 1

                            # --- resources: the database holds the repairs ---
                            for resource in lesson.get("resources") or []:
                                slug = resource.get("slug")
                                current = live.get(slug)
                                if not slug or current is None:
                                    continue
                                for field in RESOURCE_FIELDS:
                                    new = current.get(field)
                                    old = resource.get(field)
                                    if new == old:
                                        continue
                                    # Never blank a manifest value from a NULL
                                    # column: absent in the DB does not mean
                                    # "delete what the manifest recorded".
                                    if new in (None, "") and old not in (None, ""):
                                        if field != "section":
                                            continue
                                    changes.append(
                                        {
                                            "file": rel,
                                            "topic": topic_slug,
                                            "resource": slug,
                                            "field": field,
                                            "from": old,
                                            "to": new,
                                        }
                                    )
                                    if new in (None, ""):
                                        resource.pop(field, None)
                                    else:
                                        resource[field] = new
                                    dirty = True
                                    touched_files[rel] += 1

        if dirty and not dry_run:
            path.write_text(
                yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
                encoding="utf-8",
            )

    conn.close()
    return {
        "resource_field_changes": changes,
        "question_field_changes": question_edits,
        "question_blocks_stripped": stripped,
        "questions_removed": sum(item["removed"] for item in stripped),
        "files_touched": dict(touched_files),
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = sync(args.dry_run)

    by_field = Counter(item["field"] for item in report["resource_field_changes"])
    print(f"resource fields to update: {len(report['resource_field_changes'])}")
    for field, count in by_field.most_common():
        print(f"  {field}: {count}")
    print(
        f"\nmanifest question blocks to strip: {len(report['question_blocks_stripped'])} "
        f"({report['questions_removed']} questions, now owned by content/questions/)"
    )
    print(f"files touched: {len(report['files_touched'])}")
    for name, count in sorted(report["files_touched"].items()):
        print(f"  {name}: {count} change(s)")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "manifest_sync.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.dry_run:
        print("\ndry run — nothing written")
    else:
        print("\nmanifests updated; re-run import_curriculum and the content should not move")


if __name__ == "__main__":
    main()
