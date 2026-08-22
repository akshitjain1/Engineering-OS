"""Strict readiness contract for Engineering OS trustworthiness lockdown.

READY is earned only when every condition below holds.
PARTIAL_COVERAGE / NEEDS_REVIEW / VERIFIED / TRUSTED / HTTP200 never imply READY.

Resource coverage must be resource-specific (stored on the resource), never
copied from topic.required at evaluation time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.content.verification import (
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    EXACTNESS_MULTI_TOPIC,
    PRACTICE_GAP,
    PRACTICE_NO_PRACTICE_REQUIRED,
    PRACTICE_UNVERIFIED,
    PRACTICE_VERIFIED,
    READINESS_BROKEN,
    READINESS_NEEDS_REVIEW,
    READINESS_PARTIAL_COVERAGE,
    READINESS_PRACTICE_GAP,
    READINESS_PRACTICE_UNVERIFIED,
    READINESS_READY,
    READINESS_RESOURCE_GAP,
    READINESS_TIME_UNVERIFIED,
    VERIFICATION_BROKEN,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
)

# Statuses that may contribute verified concept coverage toward READY
_COVERAGE_OK = frozenset({VERIFICATION_VERIFIED_COVERAGE})
# Statuses that block READY if present on any PRIMARY
_BLOCKING_PRIMARY = frozenset(
    {
        VERIFICATION_BROKEN,
        "BROKEN",
        VERIFICATION_NEEDS_REVIEW,
        "NEEDS_REVIEW",
        VERIFICATION_UNVERIFIED,
        "UNVERIFIED",
        "UNRESOLVED",
        "VERIFIED",  # legacy HTTPS-only — not content verification
        "TRUSTED",
        VERIFICATION_COLLECTION_ONLY,
        "COLLECTION_ONLY",
    }
)


@dataclass
class ReadinessDecision:
    readiness: str
    notes: str
    contradictions: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)


def _norm_status(status: Optional[str]) -> str:
    s = (status or VERIFICATION_UNVERIFIED).upper()
    if s == "VERIFIED":
        return "VERIFIED"  # legacy — not VERIFIED_COVERAGE
    if s == "TRUSTED":
        return "TRUSTED"
    return s


def _resource_covered(r: Any) -> set[str]:
    return {str(c).strip() for c in (getattr(r, "required_concepts_covered", None) or []) if str(c).strip()}


def _has_evidence(r: Any) -> bool:
    """Evidence record required for VERIFIED_COVERAGE claims."""
    ev = getattr(r, "verification_evidence", None)
    if ev and str(ev).strip() not in ("", "{}", "null", "None"):
        return True
    # Domain0 manifest rows store notes mentioning inspection
    notes = (getattr(r, "notes", None) or "").lower()
    if "domain0" in notes or "manifest" in notes or "content inspection" in notes:
        return True
    return False


def evaluate_readiness(
    *,
    required_concepts: list[str],
    primaries: list[Any],
    practice_status: str,
    practice_compatible: bool,
    practice_gap_detail: Optional[str],
    existing_minutes: Optional[int],
    awareness_only: bool = False,
) -> ReadinessDecision:
    checks: dict[str, bool] = {}
    contradictions: list[str] = []

    concept_contract_valid = bool(required_concepts) or awareness_only
    checks["concept_contract_valid"] = concept_contract_valid

    primary_exists = bool(primaries)
    checks["primary_exists"] = primary_exists

    if not primary_exists:
        return ReadinessDecision(
            READINESS_RESOURCE_GAP,
            "No PRIMARY learning resource.",
            contradictions,
            checks,
        )

    statuses = [_norm_status(getattr(r, "verification_status", None)) for r in primaries]
    exactnesses = [(getattr(r, "exactness", None) or "").upper() for r in primaries]

    primary_live = not any(s in (VERIFICATION_BROKEN, "BROKEN") for s in statuses)
    checks["primary_live"] = primary_live

    # Collection without navigation cannot be the sole path to READY
    collection_block = any(
        (ex == EXACTNESS_COLLECTION or st == VERIFICATION_COLLECTION_ONLY)
        and not (getattr(r, "section", None) or getattr(r, "lecture", None))
        for r, ex, st in zip(primaries, exactnesses, statuses)
    )
    checks["not_collection_without_nav"] = not collection_block

    multi_without_nav = any(
        ex == EXACTNESS_MULTI_TOPIC and not (getattr(r, "section", None) or getattr(r, "lecture", None))
        for r, ex in zip(primaries, exactnesses)
    )
    checks["multi_topic_has_nav"] = not multi_without_nav

    # Only VERIFIED_COVERAGE primaries contribute coverage toward READY
    verified_primaries = [
        r for r, st in zip(primaries, statuses) if st == VERIFICATION_VERIFIED_COVERAGE
    ]
    partial_primaries = [
        r for r, st in zip(primaries, statuses) if st == VERIFICATION_PARTIAL_COVERAGE
    ]

    # Coverage union from verified resources only (strict)
    verified_union: set[str] = set()
    for r in verified_primaries:
        verified_union |= _resource_covered(r)

    # Also allow PARTIAL resources' covered set for topic PARTIAL classification,
    # but not for READY (strict contract).
    any_union = set(verified_union)
    for r in partial_primaries:
        any_union |= _resource_covered(r)

    required_set = set(required_concepts)
    missing_for_ready = sorted(required_set - verified_union)
    missing_any = sorted(required_set - any_union)
    checks["coverage_complete_verified"] = not missing_for_ready and bool(required_set or awareness_only)

    # Evidence required on every VERIFIED_COVERAGE primary that claims coverage
    evidence_ok = True
    for r in verified_primaries:
        if _resource_covered(r) and not _has_evidence(r):
            evidence_ok = False
            contradictions.append(
                f"Resource {getattr(r, 'slug', '?')} claims VERIFIED_COVERAGE without evidence record"
            )
    checks["evidence_present"] = evidence_ok

    # Blocking statuses on any primary
    blocking = [s for s in statuses if s in _BLOCKING_PRIMARY]
    checks["no_blocking_primary"] = not blocking

    # PARTIAL present → cannot be READY even if joint would complete
    has_partial = bool(partial_primaries)
    checks["no_partial_primary"] = not has_partial

    # Exactness must be explicit and not COLLECTION (MULTI_TOPIC OK with nav)
    exactness_ok = all(
        ex in (EXACTNESS_EXACT, EXACTNESS_MULTI_TOPIC)
        and not (ex == EXACTNESS_COLLECTION)
        for ex in exactnesses
    ) and not collection_block
    # Also reject missing exactness
    if any(not ex for ex in exactnesses):
        exactness_ok = False
    checks["exactness_ok"] = exactness_ok and not multi_without_nav

    practice_ok = practice_status in (PRACTICE_VERIFIED, PRACTICE_NO_PRACTICE_REQUIRED) and practice_compatible
    checks["practice_ok"] = practice_ok

    time_ok = (existing_minutes is not None and existing_minutes > 0) or any(
        getattr(r, "estimated_minutes", None) for r in primaries
    )
    checks["time_ok"] = time_ok

    # --- Decision tree (truth over optimism) ---
    if not concept_contract_valid:
        return ReadinessDecision(
            READINESS_NEEDS_REVIEW,
            "No required-concept contract (and not AWARENESS_ONLY).",
            contradictions,
            checks,
        )

    if not primary_live:
        return ReadinessDecision(
            READINESS_BROKEN,
            "A PRIMARY resource is BROKEN.",
            contradictions,
            checks,
        )

    if collection_block:
        return ReadinessDecision(
            READINESS_RESOURCE_GAP,
            "PRIMARY is COLLECTION without section/timestamp.",
            contradictions,
            checks,
        )

    if multi_without_nav:
        return ReadinessDecision(
            READINESS_NEEDS_REVIEW,
            "MULTI_TOPIC PRIMARY lacks section/timestamp.",
            contradictions,
            checks,
        )

    if blocking:
        # NEEDS_REVIEW / legacy VERIFIED / TRUSTED on primary → honest NEEDS_REVIEW
        # (do NOT call this RESOURCE_GAP; a candidate resource exists but is unverified)
        soft_block = {VERIFICATION_NEEDS_REVIEW, "NEEDS_REVIEW", "VERIFIED", "TRUSTED", VERIFICATION_UNVERIFIED, "UNVERIFIED", "UNRESOLVED"}
        if any(s in soft_block for s in blocking) and not any(
            s in (VERIFICATION_BROKEN, "BROKEN") for s in statuses
        ):
            return ReadinessDecision(
                READINESS_NEEDS_REVIEW,
                f"PRIMARY not content-verified for learner trust (statuses={sorted(set(blocking))}).",
                contradictions,
                checks,
            )
        if any(s in (VERIFICATION_BROKEN, "BROKEN") for s in blocking):
            return ReadinessDecision(
                READINESS_BROKEN,
                "A PRIMARY resource is BROKEN.",
                contradictions,
                checks,
            )

    if has_partial:
        # Joint with PARTIAL resource → topic PARTIAL even if union complete via partials
        if missing_any:
            return ReadinessDecision(
                READINESS_PARTIAL_COVERAGE,
                f"PARTIAL primary present; missing={missing_any}",
                contradictions,
                checks,
            )
        return ReadinessDecision(
            READINESS_PARTIAL_COVERAGE,
            "PRIMARY includes PARTIAL_COVERAGE; strict contract forbids READY until each covering resource is VERIFIED_COVERAGE.",
            contradictions,
            checks,
        )

    if missing_for_ready:
        if any_union and not missing_any:
            # Shouldn't happen if only verified counted and no partials
            pass
        if missing_any and any_union:
            return ReadinessDecision(
                READINESS_PARTIAL_COVERAGE,
                f"Missing required concepts: {missing_any}",
                contradictions,
                checks,
            )
        return ReadinessDecision(
            READINESS_RESOURCE_GAP,
            f"Missing required concepts under VERIFIED_COVERAGE primaries: {missing_for_ready}",
            contradictions,
            checks,
        )

    if not evidence_ok:
        return ReadinessDecision(
            READINESS_NEEDS_REVIEW,
            "Coverage claimed without verification evidence.",
            contradictions,
            checks,
        )

    if not practice_compatible or practice_status == PRACTICE_GAP:
        return ReadinessDecision(
            READINESS_PRACTICE_GAP,
            practice_gap_detail or "Practice requires untaught concepts.",
            contradictions,
            checks,
        )

    if practice_status == PRACTICE_UNVERIFIED:
        return ReadinessDecision(
            READINESS_PRACTICE_UNVERIFIED,
            "Practice destination/quantity not verified.",
            contradictions,
            checks,
        )

    if not time_ok:
        return ReadinessDecision(
            READINESS_TIME_UNVERIFIED,
            "No time estimate on lesson or PRIMARY resources.",
            contradictions,
            checks,
        )

    if not exactness_ok:
        return ReadinessDecision(
            READINESS_NEEDS_REVIEW,
            "PRIMARY exactness missing or invalid for READY.",
            contradictions,
            checks,
        )

    # All checks for READY
    if not all(
        [
            checks["concept_contract_valid"],
            checks["primary_exists"],
            checks["primary_live"],
            checks["coverage_complete_verified"],
            checks["evidence_present"],
            checks["no_blocking_primary"],
            checks["no_partial_primary"],
            checks["exactness_ok"],
            checks["practice_ok"],
            checks["time_ok"],
            checks["not_collection_without_nav"],
            checks["multi_topic_has_nav"],
        ]
    ):
        return ReadinessDecision(
            READINESS_NEEDS_REVIEW,
            f"Strict READY checks failed: {[k for k,v in checks.items() if not v]}",
            contradictions,
            checks,
        )

    return ReadinessDecision(READINESS_READY, "Strict readiness contract satisfied.", contradictions, checks)
