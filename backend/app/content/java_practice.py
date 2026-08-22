"""Explicit practice contracts for Java topics (destination + quantity)."""

from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.models import CurriculumLesson, CurriculumTopic, LessonExercise

# Default practice for any java topic without a specific override
DEFAULT = {
    "destination_type": "LOCAL_IDE",
    "destination_url": "local",
    "quantity": 2,
    "instructions": "Write 2 short Java programs that exercise this topic's learning objective. EXPECTED: compile and run cleanly.",
}

JAVA_PRACTICE: dict[str, dict] = {
    "java-jdk-jre": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 1,
        "instructions": "Install/verify JDK. Run `java -version` and `javac -version`. EXPECTED: both print versions.",
    },
    "java-first-program": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 1,
        "instructions": "Write HelloWorld.java, compile, run. EXPECTED: prints Hello World.",
    },
    "java-primitives": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 programs using int/long/double/boolean/char and print results.",
    },
    "java-arrays": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 array programs: declare, index, iterate, find max.",
    },
    "java-strings": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 String programs: concatenate, substring, compare.",
    },
    "java-classes-objects": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 2,
        "instructions": "Create 2 classes with fields/constructors; instantiate and call methods.",
    },
    "java-inheritance": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 2,
        "instructions": "Implement superclass/subclass with override; demonstrate polymorphism.",
    },
    "java-interfaces": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 2,
        "instructions": "Define an interface and 2 implementing classes; call via interface type.",
    },
    "java-try-catch": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 2,
        "instructions": "Write try/catch/finally and one exception path with meaningful messages.",
    },
    "java-list": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Use ArrayList for add/remove/iterate in 3 mini programs.",
    },
    "java-map": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Use HashMap for frequency count and lookup in 3 mini programs.",
    },
    "java-loops": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 programs: for, while, enhanced-for over an array.",
    },
    "java-if-else": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 programs using nested if/else on sample inputs.",
    },
    "java-method-basics": {
        "destination_type": "LOCAL_IDE",
        "destination_url": "local",
        "quantity": 3,
        "instructions": "Write 3 methods with parameters/return values; call from main.",
    },
}


def enrich_java_practice(db: Session) -> dict[str, int]:
    updated = 0
    created = 0
    topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.exercises))
        .filter(CurriculumTopic.domain_key == "java")
        .all()
    )
    for topic in topics:
        spec = JAVA_PRACTICE.get(topic.slug or "", DEFAULT)
        instructions = spec.get("instructions") or DEFAULT["instructions"]
        # Specialize default instruction with topic name
        if topic.slug not in JAVA_PRACTICE:
            instructions = (
                f"Write {spec['quantity']} short Java programs that practice: {topic.name}. "
                "EXPECTED: compile and run cleanly with clear output."
            )
        for les in topic.lessons:
            if les.exercises:
                ex = les.exercises[0]
                ex.destination_type = spec["destination_type"]
                ex.destination_url = spec.get("destination_url")
                ex.quantity = spec["quantity"]
                ex.practice_instructions = instructions
                ex.concepts_required = []
                updated += 1
            else:
                ex = LessonExercise(
                    slug=f"{topic.slug}-practice",
                    title=f"Practice: {topic.name}",
                    description=instructions,
                    lesson_id=les.id,
                    exercise_type="CODING",
                    destination_type=spec["destination_type"],
                    destination_url=spec.get("destination_url"),
                    quantity=spec["quantity"],
                    practice_instructions=instructions,
                    concepts_required=[],
                )
                db.add(ex)
                created += 1
    db.flush()
    return {"updated": updated, "created": created}
