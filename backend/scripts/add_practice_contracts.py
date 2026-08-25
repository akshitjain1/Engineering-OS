"""Attach practice contracts to every topic created by decompose_ai_domains.py.

Spec PART H mapping (depth_target -> practice type):
  AWARENESS       -> RECALL
  INTUITION       -> EXPLAIN
  MECHANICS       -> TRACE (or PREDICT_OUTPUT for numeric topics)
  IMPLEMENTATION  -> IMPLEMENT
  APPLICATION     -> SOLVE
  PROJECT         -> PROJECT

Every contract has: objective, concepts_required, quantity, explicit
destination, estimated minutes, completion criteria, difficulty.
Idempotent: skips lessons that already have exercises.
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumLesson, LessonExercise

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

DEPTH_TO_TYPE = {
    "AWARENESS": "RECALL",
    "INTUITION": "EXPLAIN",
    "MECHANICS": "TRACE",
    "IMPLEMENTATION": "IMPLEMENT",
    "APPLICATION": "SOLVE",
    "PROJECT": "PROJECT",
}

PREDICT_OUTPUT_SLUGS = {
    "dl-forward-propagation", "dl-convolution-op", "dl-padding-stride", "cv-bounding-boxes-iou",
}


def build_contract(topic: CurriculumLesson) -> dict | None:
    slug = None
    return None


def main() -> None:
    db = SessionLocal()
    created = []
    skipped = []
    try:
        topics = db.query(CurriculumTopic).all()
        lessons_by_topic: dict[int, list[CurriculumLesson]] = {}
        for l in db.query(CurriculumLesson).all():
            lessons_by_topic.setdefault(l.topic_id, []).append(l)
        existing_exercise_lessons = {row[0] for row in db.query(LessonExercise.lesson_id).all()}

        for t in topics:
            slug = t.slug or ""
            # Only the decomposition-created topics (identifiable by domain_key + our slug space)
            decomposed_prefixes = (
                "math-", "ml-", "dl-", "cv-", "nlp-", "genai-", "ai-eng-"
            )
            if not slug.startswith(decomposed_prefixes):
                continue
            depth = (t.depth_target or "WORKING_KNOWLEDGE").upper()
            ptype = DEPTH_TO_TYPE.get(depth)
            if ptype == "TRACE" and slug in PREDICT_OUTPUT_SLUGS:
                ptype = "PREDICT_OUTPUT"
            tls = sorted(lessons_by_topic.get(t.id, []), key=lambda x: x.order_index)
            if not tls:
                skipped.append(slug + "::no-lesson")
                continue
            lesson = tls[0]
            if lesson.id in existing_exercise_lessons:
                skipped.append(slug + "::has-exercises")
                continue

            name = t.name
            minutes = max(10, int((t.estimated_minutes or 20) * 0.4))
            contracts = {
                "RECALL": dict(
                    title=f"Recall check: {name}",
                    description=f"From memory, list the key ideas of {name}. Then check against the source.",
                    instructions=(
                        f"Close all notes. Write 3 bullet points answering: what problem does "
                        f"{name} address, and what is its core idea? Reopen the source only after "
                        f"writing. Completion criteria: your bullets cover the same core ideas as "
                        f"the source."
                    ),
                    dest=("SELF_CHECK", None), qty=1,
                    criteria="Bullets match source's core ideas before reopening notes.",
                ),
                "EXPLAIN": dict(
                    title=f"Explain: {name}",
                    description=f"Explain {name} to a smart beginner in your own words.",
                    instructions=(
                        f"Write a 5-sentence explanation of {name}: (1) the problem it solves, "
                        f"(2) the mechanism in plain words, (3) one concrete example, (4) one "
                        f"misconception people have, (5) when NOT to use it. Completion criteria: "
                        f"a friend unfamiliar with the topic could follow all five sentences."
                    ),
                    dest=("SELF_CHECK", None), qty=1,
                    criteria="Five sentences written covering problem/mechanism/example/misconception/limits.",
                ),
                "TRACE": dict(
                    title=f"Trace: {name}",
                    description=f"Trace a small concrete case through {name} step by step.",
                    instructions=(
                        f"On paper, trace ONE tiny concrete example through the mechanics of "
                        f"{name}, showing every intermediate value/state. Use inputs small enough "
                        f"to compute by hand. Completion criteria: every intermediate value shown "
                        f"and final result consistent."
                    ),
                    dest=("SELF_CHECK", None), qty=1,
                    criteria="Full hand-trace of one example with intermediates.",
                ),
                "PREDICT_OUTPUT": dict(
                    title=f"Predict output: {name}",
                    description=f"Predict outputs for 2 small cases using {name}.",
                    instructions=(
                        f"For two different small inputs, PREDICT the output that {name} would "
                        f"produce BEFORE computing/checking. Then verify each prediction. "
                        f"Completion criteria: both predictions verified; wrong ones re-derived."
                    ),
                    dest=("SELF_CHECK", None), qty=2,
                    criteria="Two predictions made then verified.",
                ),
                "IMPLEMENT": dict(
                    title=f"Implement: {name}",
                    description=f"Build a minimal working version of {name}.",
                    instructions=(
                        f"Write code implementing the core of {name} from scratch (no copy-paste): "
                        f"smallest version that runs on toy data. Completion criteria: code runs "
                        f"on one hand-checkable example and matches your hand-trace."
                    ),
                    dest=("CODE_SANDBOX", None), qty=1,
                    criteria="Minimal implementation runs and matches hand-trace.",
                ),
                "SOLVE": dict(
                    title=f"Apply: {name}",
                    description=f"Solve one realistic mini-task using {name}.",
                    instructions=(
                        f"Take a small real-ish dataset/problem and apply {name} end to end once: "
                        f"prepare input, run the method, interpret the result in one sentence. "
                        f"Completion criteria: result produced and interpretation written."
                    ),
                    dest=("NOTEBOOK", None), qty=1,
                    criteria="One end-to-end application with written interpretation.",
                ),
                "PROJECT": dict(
                    title=f"Mini project: {name}",
                    description=f"{name}: complete a scoped end-to-end build.",
                    instructions=(
                        f"Complete the scoped project for {name}: pick a dataset/task, prepare "
                        f"data, train/build, evaluate honestly, and write a 5-line reflection on "
                        f"what worked and what you would change. Completion criteria: artifact + "
                        f"reflection exist."
                    ),
                    dest=("PROJECT_REPO", None), qty=1,
                    criteria="Working artifact plus written reflection delivered.",
                ),
            }
            c = contracts[ptype]
            ex = LessonExercise(
                slug=f"{slug}-practice",
                title=c["title"],
                description=c["description"],
                difficulty="beginner" if depth in ("AWARENESS", "INTUITION") else "intermediate",
                topic=name,
                lesson_id=lesson.id,
                exercise_type=ptype,
                destination_type=c["dest"][0],
                destination_url=None,
                quantity=c["qty"],
                concepts_required=[slug],
                practice_instructions=c["instructions"],
            )
            db.add(ex)
            existing_exercise_lessons.add(lesson.id)
            created.append({"slug": slug, "type": ptype, "minutes_estimate": minutes})

        db.commit()
        out = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "created": len(created),
            "by_type": {},
            "skipped_count": len(skipped),
        }
        for c in created:
            out["by_type"][c["type"]] = out["by_type"].get(c["type"], 0) + 1
        json.dump({**out, "detail": created, "skipped": skipped},
                  open(f"{REPORT_DIR}\\practice_contracts_log.json", "w", encoding="utf-8"), indent=2)
        print(json.dumps(out, indent=2))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
