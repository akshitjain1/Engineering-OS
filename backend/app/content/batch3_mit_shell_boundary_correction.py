"""Correct Batch 3 learner boundaries and instructions without changing mappings."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


CORRECTIONS: dict[str, dict[str, str]] = {
    "cf-shell": {
        "boundary": '"Topic 1: The Shell" through "Why should you care about it?"',
        "instruction": "Study what a shell is, why command-line interfaces matter, and how the shell fits between the learner and operating-system programs.",
    },
    "cf-command-line": {
        "boundary": '"Navigating in the shell" through the first command/argument examples',
        "instruction": "Focus on how the shell parses a command, executes a program, passes arguments, and represents the current working directory.",
    },
    "cf-filesystem-navigation": {
        "boundary": '"Navigating in the shell"',
        "instruction": "Study pwd, cd, absolute paths, relative paths, ., .., and how the current working directory affects relative paths.",
    },
    "cf-linux-files": {
        "boundary": '"What is available in the shell?"',
        "instruction": "Focus on basic file/directory commands: cat, sort, uniq, head, tail, sed, find and related command-line file manipulation/discovery concepts.",
    },
    "cf-pipes": {
        "boundary": '"The shell language (bash)"',
        "instruction": "Focus specifically on the pipe operator |, stdin/stdout streams, and how the shell connects the output of one process to the input of another.",
    },
    "cf-redirection": {
        "boundary": '"The shell language (bash)"',
        "instruction": "Focus specifically on >, >>, <, stdout, stderr, and tee. Understand the difference between piping data to another program and redirecting it to a file.",
    },
    "cf-grep": {
        "boundary": '"What is available in the shell?"',
        "instruction": "Focus only on grep: searching text, regular-expression patterns, recursive searching, and using grep inside pipelines.",
    },
    "cf-find": {
        "boundary": '"What is available in the shell?"',
        "instruction": "Focus only on find: recursive file discovery, predicates such as -type/-name, and combining find with other command-line tools.",
    },
    "cf-linux-permissions": {
        "boundary": '"Files and Permissions"',
        "instruction": "Study Unix file permissions, users/groups, read/write/execute bits, and how permissions control access.",
    },
    "cf-linux-processes": {
        "boundary": '"Signals and Job Control"',
        "instruction": "Study processes, signals, Ctrl-C, Ctrl-Z, jobs, fg, bg, kill, and basic foreground/background process control.",
    },
}


def _resolve(db: Session, slug: str) -> CurriculumResource:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    if not lesson:
        raise ValueError(f"Missing lesson for topic: {slug}")
    row = db.query(CurriculumResource).filter(
        CurriculumResource.lesson_id == lesson.id,
        CurriculumResource.role == "PRIMARY",
        CurriculumResource.learner_visible.is_(True),
    ).first()
    if not row:
        raise ValueError(f"Missing learner-visible PRIMARY for {slug}")
    return row


def apply_boundary_corrections(db: Session, *, commit: bool = True) -> dict[str, Any]:
    changed = []
    for slug, correction in CORRECTIONS.items():
        row = _resolve(db, slug)
        protected = {"url": row.url, "provider": row.provider, "role": row.role, "learner_visible": row.learner_visible, "slug": row.slug}
        row.section = correction["boundary"]
        row.start_boundary = correction["boundary"]
        row.end_boundary = correction["boundary"]
        row.description = correction["instruction"]
        changed.append({"topic": slug, "resource": row.slug, "protected": protected, "boundary": correction["boundary"], "instruction": correction["instruction"]})
    if commit:
        db.commit()
    return {"processed": len(changed), "changed": changed}