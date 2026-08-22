"""Load unified concept contracts for all topics.

Merges Domain 0 DEMO_CONCEPT_REGISTRY with generated JSON contracts.
Never copies topic.required into resource coverage — that happens only via
content inspection / RESOURCE_COVERAGE_MANIFEST.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.content.verification import Concept, TopicConcepts, DEMO_CONCEPT_REGISTRY

DATA_PATH = Path(__file__).resolve().parent / "data" / "concept_contracts.json"


@lru_cache(maxsize=1)
def load_contract_payload() -> dict:
    if not DATA_PATH.exists():
        return {"contracts": {}, "topic_count": 0}
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def get_topic_concepts(topic_slug: str) -> Optional[TopicConcepts]:
    """Prefer Domain 0 registry; else JSON contracts."""
    if topic_slug in DEMO_CONCEPT_REGISTRY:
        return DEMO_CONCEPT_REGISTRY[topic_slug]
    payload = load_contract_payload()
    raw = (payload.get("contracts") or {}).get(topic_slug)
    if not raw:
        return None
    required = [
        Concept(slug=c["slug"], name=c.get("description") or c["slug"])
        for c in raw.get("required") or []
    ]
    optional = [
        Concept(slug=c["slug"], name=c.get("description") or c["slug"], importance="OPTIONAL")
        for c in raw.get("optional") or []
    ]
    return TopicConcepts(topic_slug=topic_slug, required=required, optional=optional)


def get_evidence_terms(topic_slug: str, concept_slug: str) -> list[str]:
    if topic_slug in DEMO_CONCEPT_REGISTRY:
        for c in DEMO_CONCEPT_REGISTRY[topic_slug].required:
            if c.slug == concept_slug:
                # Independent terms from concept name/slug — not the full required list
                parts = re_split_terms(c.name) + re_split_terms(c.slug.replace("-", " "))
                return parts[:12]
    payload = load_contract_payload()
    raw = (payload.get("contracts") or {}).get(topic_slug) or {}
    for c in raw.get("required") or []:
        if c.get("slug") == concept_slug:
            return list(c.get("evidence_terms") or [])[:12]
    return []


def re_split_terms(text: str) -> list[str]:
    import re

    stop = {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as",
        "is", "are", "be", "by", "from", "that", "this", "you", "your", "vs", "via",
    }
    out = []
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9+#.]{1,}", text or ""):
        low = tok.lower()
        if low not in stop and len(low) >= 2:
            out.append(low)
    return out


def all_contract_slugs() -> set[str]:
    slugs = set(DEMO_CONCEPT_REGISTRY.keys())
    payload = load_contract_payload()
    slugs.update((payload.get("contracts") or {}).keys())
    return slugs


def contract_count() -> int:
    return len(all_contract_slugs())
