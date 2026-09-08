"""Generate a per-module authoring brief for question banks.

An author -- human or agent -- writing self-check questions for a topic needs
to know two things: what the topic is meant to teach, and which page the app
tells the learner to open. Questions written without the second are how a
Knapsack page ended up asking about memoisation in general.

Writes one Markdown brief per module to ``reports/question_briefs/``.

Run:
    python -m app.content.question_briefs
    python -m app.content.question_briefs mod-cv mod-dl-core
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
OUT_DIR = BACKEND / "reports" / "question_briefs"

TOPIC_SQL = """
    SELECT t.id, t.slug, t.name, t.description, t.depth_target, t.learning_track,
           m.slug AS module_slug, m.name AS module_name, s.name AS subject_name,
           (SELECT COUNT(*) FROM curriculum_lessons l
              JOIN lesson_questions q ON q.lesson_id = l.id
             WHERE l.topic_id = t.id) AS question_count
      FROM curriculum_topics t
      JOIN curriculum_modules m ON t.module_id = m.id
      JOIN curriculum_subjects s ON m.subject_id = s.id
     WHERE m.slug = ?
     ORDER BY t.order_index
"""

RESOURCE_SQL = """
    SELECT r.role, r.title, r.provider, r.url, r.section, r.lecture, r.estimated_minutes
      FROM curriculum_lessons l
      JOIN curriculum_resources r ON r.lesson_id = l.id
     WHERE l.topic_id = ?
     ORDER BY CASE UPPER(COALESCE(r.role, '')) WHEN 'PRIMARY' THEN 0 ELSE 1 END,
              r.order_index
"""

EXISTING_SQL = """
    SELECT q.question, q.options
      FROM curriculum_lessons l
      JOIN lesson_questions q ON q.lesson_id = l.id
     WHERE l.topic_id = ?
     ORDER BY q.id
"""


def objective(description: str | None) -> str:
    """Pull the stated Objective line out of a topic description."""
    if not description:
        return ""
    match = re.search(r"Objective:\s*(.+?)(?:\n|$)", description)
    if match:
        return match.group(1).strip()
    return re.sub(r"\s+", " ", description).strip()[:300]


def orientation(description: str | None) -> str:
    """The prose before the Objective line: what this topic assumes and covers."""
    if not description:
        return ""
    head = re.split(r"\n\s*Objective:", description)[0]
    return re.sub(r"\s+", " ", head).strip()[:600]


def build_brief(conn: sqlite3.Connection, module_slug: str) -> tuple[str, int]:
    conn.row_factory = sqlite3.Row
    topics = list(conn.execute(TOPIC_SQL, (module_slug,)))
    if not topics:
        raise SystemExit(f"no topics found for module {module_slug!r}")

    head = topics[0]
    lines = [
        f"# Question brief: {head['module_name']} (`{module_slug}`)",
        "",
        f"Subject: {head['subject_name']}",
        f"Topics: {len(topics)}",
        "",
        "For each topic below, write at least 4 self-check questions in",
        f"`content/questions/{module_slug}.yaml`. Ground every question in the PRIMARY",
        "resource listed for that topic: the learner will have just read that page, and the",
        "question exists to check they took the right thing from it.",
        "",
        "---",
        "",
    ]

    for topic in topics:
        resources = list(conn.execute(RESOURCE_SQL, (topic["id"],)))
        existing = list(conn.execute(EXISTING_SQL, (topic["id"],)))

        lines.append(f"## `{topic['slug']}` — {topic['name']}")
        lines.append("")
        lines.append(f"- Depth target: {topic['depth_target']}  ·  Track: {topic['learning_track']}")
        obj = objective(topic["description"])
        if obj:
            lines.append(f"- Objective: {obj}")
        orient = orientation(topic["description"])
        if orient and orient != obj:
            lines.append(f"- Context: {orient}")

        if resources:
            lines.append("- Resources:")
            for res in resources:
                where = " · ".join(
                    part
                    for part in [res["lecture"] or "", res["section"] or ""]
                    if part and part != "FULL_SINGLE_PAGE"
                )
                minutes = f" (~{res['estimated_minutes']} min)" if res["estimated_minutes"] else ""
                lines.append(
                    f"  - **{(res['role'] or 'REFERENCE')}** {res['provider'] or '?'} — "
                    f"{res['title']}{minutes}"
                )
                lines.append(f"    {res['url']}")
                if where:
                    lines.append(f"    exact part: {where}")
        else:
            lines.append("- Resources: **none mapped**")

        if existing:
            lines.append(f"- Currently has {len(existing)} question(s), to be replaced:")
            for row in existing[:3]:
                filler = "  <- template filler" if row["options"] and "vague buzzword" in row["options"] else ""
                lines.append(f"  - {row['question']}{filler}")
            if len(existing) > 3:
                lines.append(f"  - ... and {len(existing) - 3} more")
        else:
            lines.append("- Currently has **no questions at all**.")
        lines.append("")

    return "\n".join(lines) + "\n", len(topics)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="*", help="module slugs; default: every module")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    modules = args.modules or [
        row["slug"] for row in conn.execute("SELECT slug FROM curriculum_modules ORDER BY slug")
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for module_slug in modules:
        text, count = build_brief(conn, module_slug)
        path = OUT_DIR / f"{module_slug}.md"
        path.write_text(text, encoding="utf-8")
        print(f"{module_slug}: {count} topics -> {path.relative_to(BACKEND)}")


if __name__ == "__main__":
    main()
