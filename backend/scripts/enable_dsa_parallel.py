"""Enable Java∥DSA early parallelism (spec Phase 2) via SPECIALIZATION lane.

Computes the prerequisite ancestor-closure of the DSA gate
{cf-time-complexity-intro, java-method-basics} plus the java runway chain,
and flips exactly those topics to learning_track='SPECIALIZATION'.

Result: while the CORE cursor walks the remaining CS-foundations block,
the parallel slot advances the runway daily → java-method-basics +
complexity-intro complete well inside a month → DSA unlocks early.

Additive/idempotent; prereqs, order, progress untouched.
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

GATE_CF_ANCESTORS = {
    # Late-cf REQUIRED ancestors gating the DSA entry:
    "cf-debugging-thinking",
    "cf-time-complexity-intro",
    "cf-space-complexity-intro",
    "cf-dependency-management",
}
JAVA_RUNWAY = {
    "java-jdk-jre", "java-first-program", "java-compile-and-run",
    "java-primitives", "java-type-conversion", "java-console-io",
    "java-operators", "java-if-else", "java-switch", "java-loops",
    "java-break-continue", "java-method-basics",
}
FLIP = GATE_CF_ANCESTORS | JAVA_RUNWAY


def ref_slug(ref):
    return ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))


def main() -> None:
    db = SessionLocal()
    try:
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}

        # 1) Revert any over-broad SPECIALIZATION marks from earlier runs
        #    (everything except the DSA runway six and the target set).
        KEEP = FLIP | {
            "dsa-algorithmic-thinking", "dsa-big-o", "dsa-best-worst-average",
            "dsa-array-traversal", "dsa-array-insert-delete", "dsa-array-patterns",
        }
        reverted = []
        for slug, t in topics.items():
            if t.learning_track == "SPECIALIZATION" and slug not in KEEP:
                t.learning_track = "CORE"
                reverted.append(slug)

        # 2) Apply the targeted runway flip.
        flipped = []
        for slug in sorted(FLIP):
            t = topics.get(slug)
            if t is None:
                continue
            if t.learning_track != "SPECIALIZATION":
                t.learning_track = "SPECIALIZATION"
                flipped.append(slug)
        db.commit()

        out = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "reverted_to_core": sorted(reverted),
            "flipped_to_specialization": sorted(flipped),
        }
        json.dump(out, open(f"{REPORT_DIR}\\dsa_parallel_track_log.json", "w", encoding="utf-8"), indent=2)
        print(json.dumps(out, indent=2))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
