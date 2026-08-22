"""Generate atomic concept contracts for every curriculum topic from YAML.

Rules:
- Concepts derived from learning_objective + mastery_criteria (not invented sprawl).
- Skip score/quiz mastery lines.
- Domain 0 contracts already in DEMO_CONCEPT_REGISTRY take precedence (never overwrite).
- Output is JSON only — does not mutate curriculum graph/YAML.

Writes: app/content/data/concept_contracts.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from app.content.verification import DEMO_CONCEPT_REGISTRY  # noqa: E402

SKIP_PATTERNS = [
    re.compile(r"score\s*>=", re.I),
    re.compile(r"topic questions", re.I),
    re.compile(r"mapped practice", re.I),
    re.compile(r"practice checklist", re.I),
    re.compile(r"complete the mapped", re.I),
    re.compile(r"stated quantity", re.I),
    re.compile(r"neetcode", re.I),
    re.compile(r"representative\s+\d", re.I),
    re.compile(r"problems?\s+in\s+the", re.I),
    re.compile(r"c-equivalent", re.I),
    re.compile(r"c equivalent", re.I),
    re.compile(r"leetcode", re.I),
    re.compile(r"solve\s+\d+", re.I),
    re.compile(r"\d+\s*[-–]\s*\d+\s+.*(problem|exercise)", re.I),
]


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


def _slugify(text: str, prefix: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > 48:
        s = s[:48].rstrip("-")
    if not s:
        s = "concept"
    return f"{prefix}-{s}"


def _evidence_terms(*texts: str) -> list[str]:
    stop = {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as",
        "is", "are", "be", "by", "from", "that", "this", "you", "your", "vs", "via",
        "how", "what", "when", "why", "use", "using", "used", "can", "into", "without",
        "notes", "explain", "describe", "implement", "write", "create", "print", "score",
        "topic", "questions", "install", "locate", "current", "modern", "basic", "basics",
    }
    terms: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for tok in re.findall(r"[A-Za-z][A-Za-z0-9+#.]{1,}", text or ""):
            low = tok.lower().rstrip(".")
            if low in stop or len(low) < 2:
                continue
            if low not in seen:
                seen.add(low)
                terms.append(low)
            if len(terms) >= 12:
                return terms
    return terms


def concepts_from_topic(topic: dict) -> list[dict]:
    slug = topic["slug"]
    prefix = slug if len(slug) < 40 else slug[:40]
    lo = (topic.get("learning_objective") or "").strip()
    mastery = topic.get("mastery_criteria") or []
    concepts: list[dict] = []
    seen: set[str] = set()

    def add(concept_slug: str, description: str, *term_sources: str) -> None:
        if concept_slug in seen:
            return
        seen.add(concept_slug)
        concepts.append(
            {
                "slug": concept_slug,
                "description": description[:240],
                "evidence_terms": _evidence_terms(description, *term_sources),
            }
        )

    # Prefer mastery criteria that state skills (skip pure quiz/practice lines)
    for crit in mastery:
        c = (crit or "").strip()
        if not c:
            continue
        if any(p.search(c) for p in SKIP_PATTERNS):
            continue
        # Strip "without notes" suffix for cleaner description
        clean = re.sub(r"\s*without notes\.?$", "", c, flags=re.I).strip()
        # Derive short slug from first meaningful phrase
        short = re.sub(
            r"^(Explain|Describe|Implement|Write|Create|Install|Locate|Verify|Apply|Use|Identify|Compare|State|Trace|Solve)\s+",
            "",
            clean,
            flags=re.I,
        )
        short = short[:80]
        cslug = _slugify(short or clean, prefix)
        # Avoid collision
        base = cslug
        i = 2
        while cslug in seen:
            cslug = f"{base}-{i}"
            i += 1
        # Evidence terms: prefer topic name tokens + key nouns from criterion
        name_terms = _evidence_terms(topic.get("name") or "", lo)
        crit_terms = _evidence_terms(clean)
        # Merge unique, topic name first for better page matching
        merged = []
        for t in name_terms + crit_terms:
            if t not in merged:
                merged.append(t)
        concepts.append(
            {
                "slug": cslug,
                "description": clean[:240],
                "evidence_terms": merged[:12],
            }
        )
        seen.add(cslug)

    # Always ensure LO-derived concept exists (learning objective is the contract core)
    if lo:
        lo_slug = _slugify(lo, prefix)
        if lo_slug not in seen:
            name_terms = _evidence_terms(topic.get("name") or "", lo)
            concepts.insert(
                0,
                {
                    "slug": lo_slug,
                    "description": lo[:240],
                    "evidence_terms": name_terms[:12],
                },
            )
            seen.add(lo_slug)

    # If mastery empty or only quiz/practice lines, fall back already handled by LO
    if not concepts and (lo or topic.get("name")):
        add(f"{prefix}-core", lo or f"Understand {topic.get('name')}", topic.get("name", ""))

    # Cap at 4 atomic concepts to avoid sprawl
    return concepts[:4]


def main() -> Path:
    found: list = []
    for rel in (ROOT / "content" / "curriculum").rglob("*.yaml"):
        if rel.name == "v1-index.yaml":
            continue
        data = yaml.safe_load(rel.read_text(encoding="utf-8"))
        _walk_topics(data, found)

    by_slug: dict[str, dict] = {}
    for t in found:
        by_slug.setdefault(t["slug"], t)

    contracts: dict[str, dict] = {}
    preserved_domain0 = 0
    generated = 0
    flagged_vague = []

    for slug, topic in sorted(by_slug.items()):
        lo = (topic.get("learning_objective") or "").strip()
        if slug in DEMO_CONCEPT_REGISTRY:
            entry = DEMO_CONCEPT_REGISTRY[slug]
            contracts[slug] = {
                "topic_slug": slug,
                "learning_objective": lo,
                "source": "DOMAIN0_REGISTRY",
                "required": [
                    {
                        "slug": c.slug,
                        "description": c.name,
                        "evidence_terms": _evidence_terms(c.name, c.slug.replace("-", " ")),
                    }
                    for c in entry.required
                ],
                "optional": [{"slug": c.slug, "description": c.name} for c in entry.optional],
            }
            preserved_domain0 += 1
            continue

        req = concepts_from_topic(topic)
        if not lo:
            flagged_vague.append(slug)
        if len(lo) < 12:
            flagged_vague.append(slug)
        contracts[slug] = {
            "topic_slug": slug,
            "learning_objective": lo,
            "source": "YAML_MASTERY_DERIVED",
            "required": req,
            "optional": [],
            "flag_vague_objective": slug in flagged_vague,
        }
        generated += 1

    out = ROOT / "app" / "content" / "data" / "concept_contracts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "topic_count": len(contracts),
        "preserved_domain0": preserved_domain0,
        "generated": generated,
        "flagged_vague": sorted(set(flagged_vague)),
        "contracts": contracts,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"topics={len(contracts)} domain0={preserved_domain0} generated={generated} vague={len(set(flagged_vague))}")
    # ensure every DB topic covered later
    return out


if __name__ == "__main__":
    main()
