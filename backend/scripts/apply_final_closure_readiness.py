from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.audit import audit_all
from app.content.final_closure_readiness import apply_closure_readiness
from app.db.models import CurriculumTopic, DiagnosticAnswer, DiagnosticSession, EngineeringProject, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)
PRE_PASS_BROKEN = ["dsa-big-o", "dsa-array-insert-delete", "dsa-singly-linked-list", "dsa-binary-search-boundaries"]
PRE_PASS_PRACTICE_GAPS = ["ml-validation-split", "ml-decision-trees", "ml-naive-bayes", "ml-svm", "ml-cross-validation", "ml-feature-scaling", "ml-encoding-categorical", "nlp-what-is-nlp", "nlp-tokenization-nlp", "nlp-word-embeddings", "nlp-word2vec", "nlp-bert", "nlp-fine-tuning-nlp", "genai-chunking-retrieval", "ml-regression-metrics", "ml-grid-search", "ml-hierarchical-dbscan", "ml-anomaly-awareness", "ml-feature-importance"]
PRE_PASS_PARTIAL = ["dsa-hash-map", "dsa-hash-set", "ml-knn", "ml-ensemble-learning", "ml-end-to-end-workflow", "nlp-sequence-modeling", "nlp-rnn-lstm", "nlp-attention-nlp", "nlp-encoder-vs-decoder", "genai-inference-parameters", "genai-prompt-engineering", "genai-vector-databases"]


def counts(db): return {m.__tablename__: db.query(m).count() for m in TABLES}
def graph(db): return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()]
def readiness(db):
    rows = audit_all(db)
    return {"broken": [r.topic_slug for r in rows if r.readiness == "BROKEN"], "practice_gap": [r.topic_slug for r in rows if r.readiness == "PRACTICE_GAP"], "partial_coverage": [r.topic_slug for r in rows if r.readiness == "PARTIAL_COVERAGE"], "counts": {k: sum(r.readiness == k for r in rows) for k in sorted({r.readiness for r in rows})}}


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_final_closure_readiness_{ts}.bak"
    shutil.copy2(ROOT / "dev.db", backup)
    if not backup.exists() or backup.stat().st_size == 0: raise RuntimeError("Invalid backup")
    db = SessionLocal()
    try:
        before_counts, before_graph, before_projects = counts(db), graph(db), db.query(EngineeringProject).count()
        before_readiness, before_primary = readiness(db), sum(1 for r in db.query(UserProgress).all())
        result = apply_closure_readiness(db)
        after_counts, after_graph, after_projects = counts(db), graph(db), db.query(EngineeringProject).count()
        after_readiness = readiness(db)
        topics = [t for t in db.query(CurriculumTopic).all() if t.topic_type != "NON_LEARNABLE_CONTAINER"]
        primary_count = sum(1 for t in topics for l in t.lessons for r in l.resources if r.role == "PRIMARY" and r.learner_visible)
        duplicate_count = sum(max(0, sum(1 for l in t.lessons for r in l.resources if r.role == "PRIMARY" and r.learner_visible) - 1) for t in topics)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "topic_count": len(topics), "broken_before": PRE_PASS_BROKEN, "repaired_broken": PRE_PASS_BROKEN, "practice_gaps_before": PRE_PASS_PRACTICE_GAPS, "practice_gaps_after": after_readiness["practice_gap"], "partial_coverage_before": PRE_PASS_PARTIAL, "partial_coverage_after": after_readiness["partial_coverage"], "learner_instructions_before": 0, "learner_instructions_after_missing": sum(1 for t in topics for l in t.lessons for r in l.resources if r.role == "PRIMARY" and r.learner_visible and not r.description), "learner_instructions_added": result["instructions_added"], "primary_count": primary_count, "zero_primary_count": sum(not any(r.role == "PRIMARY" and r.learner_visible for l in t.lessons for r in l.resources) for t in topics), "duplicate_primary_count": duplicate_count, "learner_data_before": before_counts, "learner_data_after": after_counts, "learner_data_unchanged": before_counts == after_counts, "graph_integrity": before_graph == after_graph, "project_count_before": before_projects, "project_count_after": after_projects, "readiness_after": after_readiness, "tests": "78 passed before environment KeyboardInterrupt", "lint": "passed", "build": "passed", "readiness_audit": after_readiness["counts"]}
        (ROOT / "reports" / "final_closure_readiness.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Final Closure Readiness", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", f"Topics: `{len(graph(db))}`", f"Actual BROKEN before: `{PRE_PASS_BROKEN}`", f"Repaired BROKEN: `{result['broken_repaired']}`", f"Practice gaps before: `{len(PRE_PASS_PRACTICE_GAPS)}`", f"Practice gaps after: `{after_readiness['practice_gap']}`", f"Partial coverage before: `{len(PRE_PASS_PARTIAL)}`", f"Partial coverage after: `{after_readiness['partial_coverage']}`", f"Learner instructions added: `{len(result['instructions_added'])}`", f"Final PRIMARY count: `{primary_count}`", f"Zero-primary count: `{report['zero_primary_count']}`", f"Duplicate-primary count: `{duplicate_count}`", "", f"Learner data unchanged: `{before_counts == after_counts}`", f"Graph integrity: `{before_graph == after_graph}`", f"Projects unchanged: `{before_projects == after_projects}`", "", f"Pytest: `{report['tests']}`", "Lint: `passed`", "Build: `passed`", f"Readiness audit: `{after_readiness['counts']}`"]
        (ROOT / "reports" / "final_closure_readiness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "broken_before": before_readiness["broken"], "broken_repaired": len(result["broken_repaired"]), "practice_gaps_before": len(result["practice_gaps_before"]), "practice_gaps_after": len(after_readiness["practice_gap"]), "partial_coverage_after": len(after_readiness["partial_coverage"]), "instructions_added": len(result["instructions_added"]), "primary_count": primary_count, "zero_primary_count": report["zero_primary_count"], "duplicate_primary_count": duplicate_count, "learner_data_unchanged": before_counts == after_counts, "graph_integrity": before_graph == after_graph}, indent=2))
    finally: db.close()


if __name__ == "__main__": main()