"""Final acceptance gate for Engineering OS trustworthiness lockdown.

Exit 0 only when: no critical contradictions, graph valid, spine intact,
progress unchanged, tests/lint/build pass. Non-READY topics are allowed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.lockdown_normalize import apply_lockdown_normalization  # noqa: E402
from app.content.demote_weak_verification import demote_weak_verification  # noqa: E402
from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.content.verification import ensure_verification_columns  # noqa: E402
from app.db.models import (  # noqa: E402
    CurriculumResource,
    CurriculumTopic,
    TopicMastery,
    UserProgress,
    UserXP,
)
from app.db.session import SessionLocal, engine  # noqa: E402
from scripts.audit_truth_consistency import run_audit  # noqa: E402
from scripts.freeze_curriculum_snapshot import validate_dag  # noqa: E402
from scripts.learner_simulation import main as sim_main  # noqa: E402
from scripts.build_unresolved_topics import main as unresolved_main  # noqa: E402


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    # Windows: npm is often npm.cmd
    if cmd and cmd[0] == "npm" and sys.platform.startswith("win"):
        cmd = ["npm.cmd", *cmd[1:]]
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, shell=False)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def main() -> int:
    ensure_optional_columns(engine)
    ensure_verification_columns(engine)

    snap_path = ROOT / "reports" / "final_lockdown_prechange.json"
    if not snap_path.exists():
        print("MISSING prechange snapshot — run freeze_final_lockdown_snapshot.py first")
        return 1
    snap = json.loads(snap_path.read_text(encoding="utf-8"))

    db = SessionLocal()
    # Re-apply lockdown normalization (idempotent)
    apply_lockdown_normalization(db)
    demote_weak_verification(db)
    db.commit()

    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    dag = validate_dag(topics)
    progress_ok = (
        db.query(UserProgress).count() == snap["counts"]["UserProgress"]
        and db.query(TopicMastery).count() == snap["counts"]["TopicMastery"]
        and db.query(UserXP).count() == snap["counts"]["UserXP"]
    )
    topic_count_ok = db.query(CurriculumTopic).count() == snap["counts"]["CurriculumTopic"]
    spine = set(snap.get("spine_slugs") or [])
    spine_ok = len(spine) == 222 and all(
        db.query(CurriculumTopic).filter(CurriculumTopic.slug == s).first() for s in list(spine)[:50]
    )
    # prereq integrity for spine sample
    prereq_ok = True
    for row in snap["topics"]:
        if row["slug"] not in spine:
            continue
        t = db.query(CurriculumTopic).filter(CurriculumTopic.slug == row["slug"]).first()
        if not t or list(t.prerequisites or []) != list(row["prerequisites"] or []):
            prereq_ok = False
            break

    results = audit_all(db)
    readiness = dict(Counter(r.readiness for r in results))
    truth = run_audit(db)
    unresolved_main()
    sim_main()

    primaries = [
        r
        for r in db.query(CurriculumResource).all()
        if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")
    ]
    exactness = Counter((r.exactness or "NONE") for r in primaries)
    practice = Counter(r.practice_status for r in results)
    time_conf = Counter((r.estimate_confidence or "NONE") for r in results if r.readiness == "READY")

    # tests
    test_code, test_out = _run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line"],
        ROOT,
    )
    # parse passed
    passed = failed = 0
    for line in test_out.splitlines():
        if "passed" in line and "failed" not in line.lower().split("passed")[0][-20:]:
            # e.g. "159 passed"
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p == "passed":
                    try:
                        passed = int(parts[i - 1])
                    except Exception:
                        pass
        if "failed" in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p.startswith("failed"):
                    try:
                        failed = int(parts[i - 1])
                    except Exception:
                        pass

    lint_code, _ = _run(["npm", "run", "lint"], REPO / "ai-engine")
    build_code, _ = _run(["npm", "run", "build"], REPO / "ai-engine")

    sim = json.loads((ROOT / "reports" / "learner_simulation.json").read_text(encoding="utf-8"))
    sim_summary = sim.get("summary") or {}

    critical = truth.get("critical_count", 0)
    # READY must not include missing concepts
    false_ready = sum(1 for r in results if r.readiness == "READY" and r.missing_required)

    print("=" * 48)
    print("ENGINEERING OS FINAL ACCEPTANCE REPORT")
    print("=" * 48)
    print()
    print(f"TOTAL TOPICS: {len(results)}")
    print()
    for k in sorted(readiness.keys()):
        print(f"{k}: {readiness[k]}")
    print()
    print("RESOURCE QUALITY:")
    for k, v in sorted(exactness.items()):
        print(f"  {k}: {v}")
    print()
    print("PRACTICE:")
    for k, v in sorted(practice.items()):
        print(f"  {k}: {v}")
    print()
    print("TIME CONFIDENCE (READY topics):")
    for k, v in sorted(time_conf.items()):
        print(f"  {k}: {v}")
    print()
    print("GRAPH:")
    print(f"  CYCLES: {len(dag.get('cycles') or [])}")
    print(f"  MISSING PREREQUISITES: {len(dag.get('missing_prerequisites') or [])}")
    print(f"  DAG_OK: {dag.get('ok')}")
    print()
    print("LEARNER SIMULATION:")
    for name, s in sim_summary.items():
        print(f"  {name}: ready {s.get('ready_sessions')}/{s.get('total')} violations={s.get('violations')}")
    print()
    print(f"CONTRADICTIONS: {critical}")
    print(f"FALSE_READY_WITH_MISSING: {false_ready}")
    print()
    print(f"ORIGINAL SPINE 222 intact: {'PASS' if spine_ok and prereq_ok else 'FAIL'}")
    print(f"USER PROGRESS unchanged: {'PASS' if progress_ok else 'FAIL'}")
    print(f"TOPIC COUNT stable: {'PASS' if topic_count_ok else 'FAIL'}")
    print()
    print(f"TESTS: exit={test_code} (parsed passed~{passed} failed~{failed})")
    print(f"FRONTEND lint: {'PASS' if lint_code == 0 else 'FAIL'}")
    print(f"FRONTEND production build: {'PASS' if build_code == 0 else 'FAIL'}")
    print("=" * 48)

    report = {
        "readiness": readiness,
        "critical_contradictions": critical,
        "false_ready": false_ready,
        "dag_ok": dag.get("ok"),
        "spine_ok": spine_ok and prereq_ok,
        "progress_ok": progress_ok,
        "topic_count_ok": topic_count_ok,
        "test_exit": test_code,
        "lint_exit": lint_code,
        "build_exit": build_code,
        "simulation": sim_summary,
    }
    (ROOT / "reports" / "final_acceptance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    db.close()

    ok = (
        critical == 0
        and false_ready == 0
        and dag.get("ok")
        and spine_ok
        and prereq_ok
        and progress_ok
        and topic_count_ok
        and test_code == 0
        and lint_code == 0
        and build_code == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
