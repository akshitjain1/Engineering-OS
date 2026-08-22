"""Additive backfill of learning_track / depth_target on existing topics.

Does not change prerequisites, names, or progress rows.
Idempotent — safe to re-run.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import CurriculumTopic

# Git / CLI / debugging / tooling → ALWAYS_ON + parallel_eligible
ALWAYS_ON_SLUGS = frozenset(
    {
        "cf-shell",
        "cf-command-line",
        "cf-filesystem-navigation",
        "cf-linux-files",
        "cf-pipes",
        "cf-redirection",
        "cf-grep",
        "cf-find",
        "cf-linux-permissions",
        "cf-linux-processes",
        "cf-package-management",
        "cf-linux-environment-variables",
        "cf-os-environment-variables",
        "cf-repository",
        "cf-commits",
        "cf-branches",
        "cf-merge",
        "cf-rebase",
        "cf-remote",
        "cf-pull-push",
        "cf-conflicts",
        "cf-reset-revert",
        "cf-cherry-pick",
        "cf-stash",
        "cf-github-workflow",
        "cf-ide",
        "cf-dev-compiler",
        "cf-debugger",
        "cf-formatter",
        "cf-linter",
        "cf-dev-package-manager",
        "cf-build-system",
        "cf-dependency-management",
        "cf-debugging-thinking",
    }
)


def _domain_key(slug: str) -> str:
    if slug.startswith("java-"):
        return "java"
    if slug.startswith("dsa-"):
        return "dsa"
    if slug.startswith("se-") or slug.startswith("soft-"):
        return "software-engineering"
    if slug.startswith("db-") or slug.startswith("be-"):
        return "backend"
    if slug.startswith("math-"):
        return "mathematics"
    if slug.startswith("ml-"):
        return "ml"
    return "foundations"


def _depth_for(slug: str, track: str) -> str:
    if track == "ALWAYS_ON":
        return "WORKING_KNOWLEDGE"
    if slug.startswith("java-") or slug.startswith("dsa-"):
        return "STRONG"
    return "WORKING_KNOWLEDGE"


def backfill_topic_tracks(db: Session) -> dict[str, int]:
    """Set learning_track / depth / parallel / domain_key on original spine rows.

    Only mutates cf-/java-/dsa- topics. Newer YAML domains keep importer values.
    """
    stats = {"updated": 0, "always_on": 0, "core": 0, "unchanged": 0, "skipped_new": 0}
    topics = db.query(CurriculumTopic).all()
    for topic in topics:
        slug = topic.slug or ""
        if not slug:
            stats["unchanged"] += 1
            continue
        # Preserve wave expansions / shells set by importer
        if not (slug.startswith("cf-") or slug.startswith("java-") or slug.startswith("dsa-")):
            stats["skipped_new"] += 1
            continue
        if slug in ALWAYS_ON_SLUGS:
            track = "ALWAYS_ON"
            parallel = True
            stats["always_on"] += 1
        else:
            track = "CORE"
            parallel = False
            stats["core"] += 1
        depth = _depth_for(slug, track)
        domain = _domain_key(slug)
        changed = (
            topic.learning_track != track
            or topic.depth_target != depth
            or bool(topic.parallel_eligible) != parallel
            or topic.domain_key != domain
        )
        if not changed:
            stats["unchanged"] += 1
            continue
        topic.learning_track = track
        topic.depth_target = depth
        topic.parallel_eligible = parallel
        topic.domain_key = domain
        stats["updated"] += 1
    db.flush()
    return stats


def run_backfill(db: Session) -> dict[str, int]:
    return backfill_topic_tracks(db)
