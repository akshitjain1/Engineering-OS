"""Phase 0 — Immutable prechange snapshot for final trustworthiness lockdown.

Does not mutate curriculum or progress.
Writes: reports/final_lockdown_prechange.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.content.verification import ensure_verification_columns  # noqa: E402
from app.db.models import (  # noqa: E402
    CurriculumResource,
    CurriculumTopic,
    EngineeringProject,
    TopicMastery,
    UserProgress,
    UserXP,
)
from app.db.session import SessionLocal, engine  # noqa: E402


def _walk_topics(node, out: list) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("topics"), list):
            for t in node["topics"]:
                if isinstance(t, dict) and t.get("slug"):
                    out.append(t)
        for v in node.values():
            _walk_topics(v, out)
    elif isinstance(node, list):
        for x in node:
            _walk_topics(x, out)


def load_yaml_next() -> dict[str, str | None]:
    found: list = []
    for rel in (ROOT / "content" / "curriculum").rglob("*.yaml"):
        if rel.name == "v1-index.yaml":
            continue
        data = yaml.safe_load(rel.read_text(encoding="utf-8"))
        _walk_topics(data, found)
    out: dict[str, str | None] = {}
    for t in found:
        out.setdefault(t["slug"], t.get("next_topic"))
    return out


def main() -> Path:
    ensure_optional_columns(engine)
    ensure_verification_columns(engine)
    db = SessionLocal()
    yaml_next = load_yaml_next()
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    spine = [
        t
        for t in topics
        if t.domain_key in ("foundations", "java", "dsa")
        and (t.slug or "").startswith(("cf-", "java-", "dsa-"))
    ]
    prereq_edges = []
    for t in topics:
        for p in t.prerequisites or []:
            prereq_edges.append({"from": t.slug, "to": p})

    snapshot = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "final_lockdown_prechange_immutable",
        "counts": {
            "CurriculumTopic": len(topics),
            "CurriculumResource": db.query(CurriculumResource).count(),
            "UserProgress": db.query(UserProgress).count(),
            "TopicMastery": db.query(TopicMastery).count(),
            "UserXP": db.query(UserXP).count(),
            "EngineeringProject": db.query(EngineeringProject).count(),
            "spine_222": len(spine),
        },
        "tracks": dict(Counter(t.learning_track for t in topics)),
        "depths": dict(Counter(t.depth_target for t in topics)),
        "domains": dict(Counter(t.domain_key or "none" for t in topics)),
        "all_topic_slugs": [t.slug for t in topics if t.slug],
        "spine_slugs": sorted(t.slug for t in spine if t.slug),
        "prerequisite_edges": prereq_edges,
        "topics": [
            {
                "slug": t.slug,
                "name": t.name,
                "order_index": t.order_index,
                "prerequisites": list(t.prerequisites or []),
                "next_topic": yaml_next.get(t.slug or ""),
                "learning_track": t.learning_track,
                "depth_target": t.depth_target,
                "domain_key": t.domain_key,
                "parallel_eligible": t.parallel_eligible,
            }
            for t in topics
        ],
    }
    out = ROOT / "reports" / "final_lockdown_prechange.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(snapshot["counts"])
    db.close()
    return out


if __name__ == "__main__":
    main()
