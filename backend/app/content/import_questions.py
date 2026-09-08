"""Load authored question banks from ``content/questions/`` into the database.

Idempotent, and non-destructive to progress: a question keeps its attempt
count and last result as long as its id does not change, so re-importing a
corrected explanation does not reset what you have already answered.

Importing a topic replaces that topic's questions. That is deliberate. The
old generated questions are the thing being fixed, and leaving them alongside
authored ones would mean the page still asks "Core idea of Knapsack?".

Run:
    python -m app.content.import_questions --dry-run
    python -m app.content.import_questions
    python -m app.content.import_questions content/questions/mod-cv.yaml
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import yaml

from app.content.question_bank import (
    QuestionBank,
    normalise_prompt,
    parse_bank,
    validate_bank,
)
from app.db.models import CurriculumLesson, CurriculumTopic, LessonQuestion
from app.db.session import SessionLocal

BACKEND = Path(__file__).resolve().parents[2]
QUESTIONS_DIR = BACKEND / "content" / "questions"
REPORTS = BACKEND / "reports"


@dataclass
class ImportReport:
    files: int = 0
    topics: int = 0
    created: int = 0
    updated: int = 0
    removed: int = 0
    history_preserved: int = 0
    errors: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        return (
            f"{self.files} file(s), {self.topics} topic(s): "
            f"{self.created} created, {self.updated} updated, {self.removed} replaced, "
            f"{self.history_preserved} kept answer history | {len(self.errors)} error(s)"
        )


def discover(paths: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml")))
        elif path.suffix in {".yaml", ".yml"}:
            found.append(path)
    return [p for p in found if not p.name.startswith("_")]


def load_bank(path: Path) -> QuestionBank:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    try:
        rel = str(path.relative_to(BACKEND)).replace("\\", "/")
    except ValueError:
        rel = str(path)
    return parse_bank(data, rel)


def _existing_prompts(db, exclude_topics: set[str]) -> dict[str, str]:
    """Normalised prompt -> topic slug, for every question already stored.

    Used to refuse a prompt that is already asked on a different topic. Topics
    being re-imported are excluded, since their own questions are about to be
    replaced.
    """
    rows = (
        db.query(LessonQuestion.question, CurriculumTopic.slug)
        .join(CurriculumLesson, LessonQuestion.lesson_id == CurriculumLesson.id)
        .join(CurriculumTopic, CurriculumLesson.topic_id == CurriculumTopic.id)
        .all()
    )
    out: dict[str, str] = {}
    for prompt, slug in rows:
        if slug in exclude_topics:
            continue
        key = normalise_prompt(prompt)
        if key:
            out.setdefault(key, slug)
    return out


def import_questions(paths: Iterable[Path], *, dry_run: bool = False) -> ImportReport:
    report = ImportReport()
    files = discover(paths)
    if not files:
        return report

    db = SessionLocal()
    try:
        topics_by_slug = {t.slug: t for t in db.query(CurriculumTopic).all() if t.slug}
        known = set(topics_by_slug)

        banks: list[QuestionBank] = []
        for path in files:
            try:
                banks.append(load_bank(path))
            except Exception as exc:
                report.errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
        report.files = len(banks)

        incoming_topics = {t.topic_slug for bank in banks for t in bank.topics}
        prompts_elsewhere = _existing_prompts(db, incoming_topics)

        for bank in banks:
            problems = validate_bank(bank, known_topics=known, prompts_elsewhere=prompts_elsewhere)
            if problems:
                report.errors.extend(problems)
                report.skipped_files.append(bank.source_path or "<bank>")
                continue
            for topic_bank in bank.topics:
                topic = topics_by_slug[topic_bank.topic_slug]
                _apply_topic(db, topic, topic_bank, report, dry_run=dry_run)
                report.topics += 1

        if dry_run:
            db.rollback()
        else:
            db.commit()
    finally:
        db.close()
    return report


def _apply_topic(db, topic: CurriculumTopic, topic_bank, report: ImportReport, *, dry_run: bool) -> None:
    lessons = (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index)
        .all()
    )
    if not lessons:
        report.errors.append(f"topic {topic.slug!r} has no lesson to attach questions to")
        return
    target = lessons[0]
    lesson_ids = [lesson.id for lesson in lessons]

    existing = db.query(LessonQuestion).filter(LessonQuestion.lesson_id.in_(lesson_ids)).all()
    by_slug = {q.slug: q for q in existing if q.slug}
    authored_ids = {q.slug for q in topic_bank.questions}

    for old in existing:
        if old.slug not in authored_ids:
            db.delete(old)
            report.removed += 1

    for index, question in enumerate(topic_bank.questions):
        row = by_slug.get(question.slug)
        if row is None:
            row = LessonQuestion(slug=question.slug, lesson_id=target.id)
            db.add(row)
            report.created += 1
        else:
            report.updated += 1
            if row.attempt_count:
                # Correcting a question must not erase what you answered.
                report.history_preserved += 1
        row.lesson_id = target.id
        row.question = question.prompt
        row.options = list(question.options)
        row.answer = question.answer
        row.explanation = question.explanation
        row.difficulty = question.difficulty
        row.topic = topic.name
        row.source = topic_bank.topic_slug
        row.mastery_requirement = question.mastery
        del index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="bank files or directories")
    parser.add_argument("--dry-run", action="store_true", help="validate and report, write nothing")
    args = parser.parse_args()

    paths = args.paths or [QUESTIONS_DIR]
    report = import_questions(paths, dry_run=args.dry_run)

    print(report.summary())
    if report.errors:
        print(f"\n{len(report.errors)} problem(s):")
        for error in report.errors[:60]:
            print(f"  - {error}")
        if len(report.errors) > 60:
            print(f"  ... and {len(report.errors) - 60} more")
    if report.skipped_files:
        print(f"\nnot imported: {', '.join(report.skipped_files)}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "question_import.json").write_text(
        json.dumps(
            {
                "files": report.files,
                "topics": report.topics,
                "created": report.created,
                "updated": report.updated,
                "removed": report.removed,
                "history_preserved": report.history_preserved,
                "errors": report.errors,
                "skipped_files": report.skipped_files,
                "dry_run": args.dry_run,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if args.dry_run:
        print("\ndry run — nothing written")


if __name__ == "__main__":
    main()
