"""Phase 0 — Freeze product structure before final content verification.

Writes reports/pre_final_lock_snapshot.json with topics, prereqs, next_topic,
tracks, depth, projects, and progress counts. Validates the DAG.
Does NOT mutate curriculum or progress.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from app.db.models import (  # noqa: E402
    CurriculumResource,
    CurriculumTopic,
    EngineeringProject,
    TopicMastery,
    UserProgress,
    UserXP,
)
from app.db.session import SessionLocal  # noqa: E402


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


def load_yaml_topics() -> dict[str, dict]:
    topics: dict[str, dict] = {}
    for rel in (ROOT / "content" / "curriculum").rglob("*.yaml"):
        if rel.name == "v1-index.yaml":
            continue
        data = yaml.safe_load(rel.read_text(encoding="utf-8"))
        found: list = []
        _walk_topics(data, found)
        for t in found:
            slug = t["slug"]
            if slug not in topics:
                topics[slug] = t
    return topics


def validate_dag(topics: list[CurriculumTopic]) -> dict:
    by_slug = {t.slug: t for t in topics if t.slug}
    missing_prereq: list[str] = []
    cycles: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(slug: str, stack: list[str]) -> None:
        if slug in visited:
            return
        if slug in visiting:
            cycles.append(" -> ".join(stack + [slug]))
            return
        visiting.add(slug)
        t = by_slug.get(slug)
        if t:
            for p in t.prerequisites or []:
                if p not in by_slug:
                    missing_prereq.append(f"{slug} -> {p}")
                else:
                    dfs(p, stack + [slug])
        visiting.discard(slug)
        visited.add(slug)

    for slug in by_slug:
        dfs(slug, [])
    return {
        "ok": not cycles and not missing_prereq,
        "cycles": cycles[:20],
        "missing_prerequisites": missing_prereq[:50],
        "topic_count": len(by_slug),
    }


def main() -> Path:
    from app.db.migrate import ensure_optional_columns
    from app.content.verification import ensure_verification_columns
    from app.db.session import engine

    ensure_optional_columns(engine)
    ensure_verification_columns(engine)

    db = SessionLocal()
    yaml_topics = load_yaml_topics()
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    projects = db.query(EngineeringProject).order_by(EngineeringProject.order_index).all()

    spine = [t for t in topics if (t.slug or "").startswith(("cf-", "java-", "dsa-"))]
    # Original spine is cf/java/dsa excluding wave expansions that also use prefixes —
    # freeze uses exact 222 from known domains foundations/java/dsa only.
    spine_222 = [
        t
        for t in topics
        if t.domain_key in ("foundations", "java", "dsa")
        and (t.slug or "").startswith(("cf-", "java-", "dsa-"))
    ]

    topic_rows = []
    for t in topics:
        yt = yaml_topics.get(t.slug or "", {})
        topic_rows.append(
            {
                "slug": t.slug,
                "name": t.name,
                "domain_key": t.domain_key,
                "learning_track": t.learning_track,
                "depth_target": t.depth_target,
                "parallel_eligible": t.parallel_eligible,
                "prerequisites": list(t.prerequisites or []),
                "next_topic": yt.get("next_topic"),
                "order_index": t.order_index,
                "estimated_minutes": t.estimated_minutes,
            }
        )

    primary_urls = []
    for r in db.query(CurriculumResource).all():
        if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
            primary_urls.append({"slug": r.slug, "url": r.url, "verification_status": r.verification_status})

    snapshot = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "CurriculumTopic": len(topics),
            "CurriculumResource": db.query(CurriculumResource).count(),
            "UserProgress": db.query(UserProgress).count(),
            "TopicMastery": db.query(TopicMastery).count(),
            "UserXP": db.query(UserXP).count(),
            "EngineeringProject": len(projects),
            "spine_domains_cf_java_dsa": len(spine_222),
            "prefix_cf_java_dsa": len(spine),
        },
        "tracks": dict(Counter(t.learning_track for t in topics)),
        "depths": dict(Counter(t.depth_target for t in topics)),
        "domains": dict(Counter(t.domain_key or "none" for t in topics)),
        "dag": validate_dag(topics),
        "topics": topic_rows,
        "spine_slugs": sorted(t.slug for t in spine_222 if t.slug),
        "projects": [
            {
                "slug": p.slug,
                "name": p.title,
                "level": p.level,
                "order_index": p.order_index,
                "prerequisites": list(p.prerequisites or []),
            }
            for p in projects
        ],
        "primary_resource_count": len(primary_urls),
    }

    out = ROOT / "reports" / "pre_final_lock_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print("counts", snapshot["counts"])
    print("dag_ok", snapshot["dag"]["ok"])
    db.close()
    return out


if __name__ == "__main__":
    main()
