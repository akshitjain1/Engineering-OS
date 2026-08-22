"""Demote weak automated keyword-match verification to NEEDS_REVIEW.

Keeps Domain0 manifest-backed VERIFIED_COVERAGE.
Does not mutate topic graph or progress.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.content.verification import (
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumResource


def _evidence_strength(row: CurriculumResource) -> str:
    """Return STRONG | WEAK | NONE."""
    ev = row.verification_evidence
    if not ev:
        notes = (row.notes or "").lower()
        if "domain0" in notes or "manifest" in notes:
            return "STRONG"
        return "NONE"
    try:
        data = json.loads(ev) if isinstance(ev, str) else ev
    except Exception:  # noqa: BLE001
        return "NONE"
    if not isinstance(data, dict):
        return "NONE"
    if data.get("source") == "RESOURCE_COVERAGE_MANIFEST":
        return "STRONG"
    if data.get("verification_method") in (
        "LOCKDOWN_CONTENT_INSPECTION_V2",
        "CONTENT_INSPECTION",
    ):
        vcs = data.get("verified_concepts") or []
        if vcs and all(
            isinstance(vc, dict)
            and (vc.get("confidence") or "") == "HIGH"
            and (vc.get("location") or vc.get("evidence"))
            for vc in vcs
        ):
            # Reject chrome-only evidence
            if any(_is_chrome_snippet(str(vc.get("evidence") or "")) for vc in vcs):
                return "WEAK"
            return "STRONG"
    vcs = data.get("verified_concepts") or []
    if not vcs:
        return "NONE"
    # Domain0 style
    if any(
        (vc.get("evidence") or "") == "DOMAIN0_MANIFEST_INSPECTION"
        or (vc.get("confidence") or "") == "HIGH"
        for vc in vcs
        if isinstance(vc, dict)
    ):
        # HIGH alone is STRONG only with location or manifest evidence
        if any((vc.get("evidence") or "") == "DOMAIN0_MANIFEST_INSPECTION" for vc in vcs if isinstance(vc, dict)):
            return "STRONG"
        if all((vc.get("location") or "") for vc in vcs if isinstance(vc, dict)):
            if any(_is_chrome_snippet(str(vc.get("evidence") or "")) for vc in vcs):
                return "WEAK"
            return "STRONG"
    # Keyword-only auto matches are WEAK
    if all(isinstance(vc, dict) and vc.get("matched_terms") for vc in vcs):
        return "WEAK"
    return "WEAK"


def _is_chrome_snippet(snippet: str) -> bool:
    s = snippet.lower()
    return any(
        x in s
        for x in (
            "skip top",
            "log in",
            "sign up",
            "navigation",
            "geeksforgeeks courses",
            "oracle university",
            "create new account",
        )
    )


def demote_weak_verification(db: Session) -> dict[str, int]:
    demoted = 0
    kept = 0
    now = datetime.now(timezone.utc).isoformat()
    for row in db.query(CurriculumResource).all():
        if (row.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN"):
            continue
        st = (row.verification_status or "").upper()
        if st not in (VERIFICATION_VERIFIED_COVERAGE, "VERIFIED", "TRUSTED"):
            continue
        strength = _evidence_strength(row)
        if strength == "STRONG":
            row.verification_status = VERIFICATION_VERIFIED_COVERAGE
            kept += 1
            continue
        # Demote weak/none — keep covered list for audit transparency but status NEEDS_REVIEW
        row.verification_status = VERIFICATION_NEEDS_REVIEW
        note = " | Lockdown: demoted weak/auto keyword verification; not learner-trusted READY"
        row.notes = ((row.notes or "") + note).strip(" |")[:500]
        row.last_verified_at = now
        demoted += 1
    db.flush()
    return {"demoted_weak": demoted, "kept_strong": kept}
