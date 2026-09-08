"""One command that says whether the curriculum's content is in good shape.

Every earlier check in this repository asked a narrow question: does this topic
have a PRIMARY, is this concept covered, is this URL alive. None of them
answered the question a learner actually has, which is *will this topic teach
me the thing it claims to*. This report gets closer to that by naming the
conditions under which it will not:

- a topic with nothing to self-check against
- a topic with fewer than four questions, which is not enough to tell knowing
  from guessing
- template filler still in the database
- one question doing duty on two topics
- study guidance that renders as a machine slug rather than a sentence
- **one resource serving several topics**, which is the root cause behind most
  of the above: if four topics send you to the same page, their questions drift
  toward being about the page rather than about the topic

Run:
    python -m app.content.content_health
    python -m app.content.content_health --module mod-cv
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"

MIN_QUESTIONS = 4

FILLER_MARKERS = ("vague buzzword", "Irrelevant outside interviews", "Replaces prerequisites")


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return list(conn.execute(sql, params))


def gather(conn: sqlite3.Connection, module: str | None = None) -> dict:
    where = "WHERE m.slug = ?" if module else ""
    params = (module,) if module else ()

    topics = _rows(
        conn,
        f"""
        SELECT t.id, t.slug, t.name, t.topic_type, t.depth_target,
               m.slug AS module_slug, s.name AS subject_name,
               (SELECT COUNT(*) FROM curriculum_lessons l
                  JOIN lesson_questions q ON q.lesson_id = l.id
                 WHERE l.topic_id = t.id) AS questions,
               (SELECT COUNT(*) FROM curriculum_lessons l
                  JOIN curriculum_resources r ON r.lesson_id = l.id
                 WHERE l.topic_id = t.id) AS resources,
               (SELECT COUNT(*) FROM curriculum_lessons l
                  JOIN curriculum_resources r ON r.lesson_id = l.id
                 WHERE l.topic_id = t.id AND UPPER(COALESCE(r.role,'')) = 'PRIMARY') AS primaries
          FROM curriculum_topics t
          JOIN curriculum_modules m ON t.module_id = m.id
          JOIN curriculum_subjects s ON m.subject_id = s.id
        {where}
         ORDER BY m.order_index, t.order_index
        """,
        params,
    )

    no_questions = [t for t in topics if t["questions"] == 0]
    thin_questions = [t for t in topics if 0 < t["questions"] < MIN_QUESTIONS]
    no_primary = [t for t in topics if t["primaries"] == 0]

    filler = _rows(
        conn,
        """
        SELECT q.id, q.question, t.slug AS topic_slug, m.slug AS module_slug
          FROM lesson_questions q
          JOIN curriculum_lessons l ON q.lesson_id = l.id
          JOIN curriculum_topics t ON l.topic_id = t.id
          JOIN curriculum_modules m ON t.module_id = m.id
         WHERE q.options LIKE '%vague buzzword%'
            OR q.question LIKE '%ore idea of%'
         ORDER BY m.slug, t.slug
        """,
    )

    shared_prompts = _rows(
        conn,
        """
        SELECT q.question, COUNT(DISTINCT t.slug) AS topics,
               GROUP_CONCAT(DISTINCT t.slug) AS slugs
          FROM lesson_questions q
          JOIN curriculum_lessons l ON q.lesson_id = l.id
          JOIN curriculum_topics t ON l.topic_id = t.id
         GROUP BY q.question
        HAVING topics > 1
         ORDER BY topics DESC
        """,
    )

    # A resource serving several topics. PRIMARY sharing is the harmful kind:
    # it means two topics send you to the same page as their main study source.
    shared_primary = _rows(
        conn,
        """
        SELECT r.url, COUNT(DISTINCT t.slug) AS topics,
               GROUP_CONCAT(DISTINCT t.slug) AS slugs
          FROM curriculum_resources r
          JOIN curriculum_lessons l ON r.lesson_id = l.id
          JOIN curriculum_topics t ON l.topic_id = t.id
         WHERE UPPER(COALESCE(r.role,'')) = 'PRIMARY'
         GROUP BY r.url
        HAVING topics > 1
         ORDER BY topics DESC, r.url
        """,
    )

    anchored = _rows(
        conn,
        """
        SELECT r.url, t.slug AS topic_slug
          FROM curriculum_resources r
          JOIN curriculum_lessons l ON r.lesson_id = l.id
          JOIN curriculum_topics t ON l.topic_id = t.id
         WHERE r.url LIKE '%#%'
        """,
    )

    raw_source = _rows(
        conn,
        """
        SELECT r.url, t.slug AS topic_slug
          FROM curriculum_resources r
          JOIN curriculum_lessons l ON r.lesson_id = l.id
          JOIN curriculum_topics t ON l.topic_id = t.id
         WHERE r.url LIKE '%raw.githubusercontent.com%'
        """,
    )

    by_module: dict[str, dict[str, int]] = defaultdict(lambda: {"topics": 0, "questions": 0, "gaps": 0})
    for topic in topics:
        entry = by_module[topic["module_slug"]]
        entry["topics"] += 1
        entry["questions"] += topic["questions"]
        if topic["questions"] < MIN_QUESTIONS:
            entry["gaps"] += 1

    return {
        "topics": len(topics),
        "questions": sum(t["questions"] for t in topics),
        "no_questions": [dict(t) for t in no_questions],
        "thin_questions": [dict(t) for t in thin_questions],
        "no_primary": [dict(t) for t in no_primary],
        "filler": [dict(r) for r in filler],
        "shared_prompts": [dict(r) for r in shared_prompts],
        "shared_primary_resources": [dict(r) for r in shared_primary],
        "anchored_urls": len(anchored),
        "raw_source_urls": [dict(r) for r in raw_source],
        "by_module": {k: v for k, v in sorted(by_module.items())},
    }


def render(report: dict) -> str:
    lines = [
        "# Curriculum content health",
        "",
        f"- Topics: **{report['topics']}**",
        f"- Questions: **{report['questions']}**",
        "",
        "| Check | Count | Healthy when |",
        "| --- | --- | --- |",
        f"| Topics with no questions | {len(report['no_questions'])} | 0 |",
        f"| Topics with fewer than {MIN_QUESTIONS} questions | {len(report['thin_questions'])} | 0 |",
        f"| Topics with no PRIMARY resource | {len(report['no_primary'])} | 0 |",
        f"| Template-filler questions | {len(report['filler'])} | 0 |",
        f"| Prompts used on more than one topic | {len(report['shared_prompts'])} | 0 |",
        f"| Raw-source URLs (render as plain text) | {len(report['raw_source_urls'])} | 0 |",
        f"| PRIMARY resources serving several topics | {len(report['shared_primary_resources'])} | as low as possible |",
        "",
    ]

    if report["no_questions"]:
        lines += ["## Topics with no questions", ""]
        for topic in report["no_questions"]:
            lines.append(f"- `{topic['slug']}` ({topic['module_slug']}) — {topic['name']}")
        lines.append("")

    if report["thin_questions"]:
        lines += [f"## Topics with fewer than {MIN_QUESTIONS} questions", ""]
        for topic in report["thin_questions"]:
            lines.append(
                f"- `{topic['slug']}` ({topic['module_slug']}) — {topic['questions']} question(s)"
            )
        lines.append("")

    if report["filler"]:
        lines += ["## Template filler still stored", ""]
        for row in report["filler"]:
            lines.append(f"- `{row['topic_slug']}` ({row['module_slug']}): {row['question']}")
        lines.append("")

    if report["shared_prompts"]:
        lines += ["## One prompt, several topics", ""]
        for row in report["shared_prompts"]:
            lines.append(f"- {row['topics']}x `{row['question'][:70]}` — {row['slugs']}")
        lines.append("")

    if report["shared_primary_resources"]:
        lines += [
            "## One PRIMARY resource, several topics",
            "",
            "Not automatically wrong: a long page legitimately serves several topics when",
            "each is pinned to its own section. It is worth reviewing though, because it is",
            "the condition under which questions drift toward being about the page rather",
            "than about the topic.",
            "",
        ]
        for row in report["shared_primary_resources"]:
            lines.append(f"- {row['topics']}x {row['url']}")
            lines.append(f"  {row['slugs']}")
        lines.append("")

    lines += ["## By module", "", "| Module | Topics | Questions | Topics short of 4 |", "| --- | --- | --- | --- |"]
    for module, stats in report["by_module"].items():
        lines.append(f"| {module} | {stats['topics']} | {stats['questions']} | {stats['gaps']} |")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", help="restrict to one module slug")
    parser.add_argument("--quiet", action="store_true", help="print the summary table only")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    report = gather(conn, args.module)

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "content_health.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    text = render(report)
    (REPORTS / "content_health.md").write_text(text, encoding="utf-8")

    if args.quiet:
        print("\n".join(text.splitlines()[:16]))
    else:
        print(text)
    print(f"wrote reports/content_health.md and content_health.json")


if __name__ == "__main__":
    main()
