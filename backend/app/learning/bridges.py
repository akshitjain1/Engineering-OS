"""Just-in-time prerequisite bridges (spec PART J).

When the learner reaches a blocked topic, return ONLY the missing REQUIRED
prerequisites with time estimates — not the entire prerequisite domain.

Supports both prerequisite formats:
- legacy: ["cf-binary"]
- enhanced: [{"slug": "math-functions", "type": "REQUIRED"}]

RECOMMENDED / AWARENESS_SAFE prereqs are surfaced as advisory only and never
block the bridge.
"""
from __future__ import annotations

from typing import Any, Optional


def _ref_slug(ref: Any) -> Optional[str]:
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        return ref.get("slug") or ref.get("topic")
    return None


def _ref_type(ref: Any) -> str:
    if isinstance(ref, dict):
        return (ref.get("type") or "REQUIRED").upper()
    return "REQUIRED"


def prerequisite_bridge(
    topic_slug: str,
    topics_by_slug: dict[str, dict[str, Any]],
    completed_slugs: set[str],
) -> dict[str, Any]:
    """Compute the minimal bridge for a topic.

    topics_by_slug: slug -> {"slug", "name", "prerequisites": list, "estimated_minutes": int|None}
    completed_slugs: slugs whose lessons are complete.
    Returns:
      {
        "topic_slug", "blocked": bool,
        "bridge": [ {slug, name, minutes, why_missing} ],
        "total_minutes": int,
        "advisory": [ ... ]  # RECOMMENDED/AWARENESS items, non-blocking
      }
    """
    topic = topics_by_slug.get(topic_slug)
    if topic is None:
        return {
            "topic_slug": topic_slug,
            "blocked": False,
            "bridge": [],
            "total_minutes": 0,
            "advisory": [],
            "error": "unknown_topic",
        }

    visited: set[str] = set()
    bridge: list[dict[str, Any]] = []
    advisory: list[dict[str, Any]] = []

    def walk(slug: str) -> None:
        if slug in visited or slug in completed_slugs:
            return
        visited.add(slug)
        node = topics_by_slug.get(slug)
        for ref in (node or {}).get("prerequisites") or []:
            child = _ref_slug(ref)
            ctype = _ref_type(ref)
            if not child:
                continue
            if ctype == "REQUIRED":
                walk(child)
                if child not in completed_slugs:
                    child_node = topics_by_slug.get(child) or {}
                    already = next((b for b in bridge if b["slug"] == child), None)
                    if already is None:
                        bridge.append(
                            {
                                "slug": child,
                                "name": child_node.get("name", child),
                                "minutes": child_node.get("estimated_minutes") or 20,
                                "why_missing": f"Required by {slug}",
                            }
                        )
            else:
                if child not in completed_slugs and all(a["slug"] != child for a in advisory):
                    child_node = topics_by_slug.get(child) or {}
                    advisory.append(
                        {
                            "slug": child,
                            "name": child_node.get("name", child),
                            "type": ctype,
                        }
                    )

    for ref in topic.get("prerequisites") or []:
        rslug = _ref_slug(ref)
        if not rslug:
            continue
        if _ref_type(ref) == "REQUIRED":
            walk(rslug)
            if rslug not in completed_slugs and all(b["slug"] != rslug for b in bridge):
                node2 = topics_by_slug.get(rslug) or {}
                bridge.insert(
                    0,
                    {
                        "slug": rslug,
                        "name": node2.get("name", rslug),
                        "minutes": node2.get("estimated_minutes") or 20,
                        "why_missing": f"Direct prerequisite of {topic_slug}",
                    },
                )
        else:
            if rslug not in completed_slugs:
                node2 = topics_by_slug.get(rslug) or {}
                advisory.append({"slug": rslug, "name": node2.get("name", rslug), "type": _ref_type(ref)})

    total = sum(b["minutes"] for b in bridge)
    return {
        "topic_slug": topic_slug,
        "blocked": len(bridge) > 0,
        "bridge": bridge,
        "total_minutes": total,
        "advisory": advisory,
    }


def centrality_map(topics_by_slug: dict[str, dict[str, Any]]) -> dict[str, int]:
    """Count direct downstream dependents per topic (revision importance input)."""
    counts: dict[str, int] = {slug: 0 for slug in topics_by_slug}
    for node in topics_by_slug.values():
        for ref in node.get("prerequisites") or []:
            s = _ref_slug(ref)
            if s in counts:
                counts[s] += 1
    return counts
