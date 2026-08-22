"""Content-based resource inspection.

Accessibility check + independent concept extraction from page text.
Does NOT copy topic.required_concepts into coverage.

A concept is marked covered only when evidence_terms for that concept
appear in the fetched content (with a surrounding evidence snippet).
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.content.concept_contracts import get_evidence_terms, get_topic_concepts
from app.content.verification import (
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    EXACTNESS_MULTI_TOPIC,
    VERIFICATION_BROKEN,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_VERIFIED_COVERAGE,
)

USER_AGENT = "EngineeringOS-Verifier/1.0 (+personal-learning; content-audit)"


@dataclass
class ConceptEvidence:
    concept: str
    evidence: str
    matched_terms: list[str] = field(default_factory=list)


@dataclass
class InspectionResult:
    resource_slug: str
    url: str
    accessible: bool
    http_status: Optional[int]
    broken: bool
    exactness: str
    verification_status: str
    covered: list[str]
    missing: list[str]
    evidence: list[ConceptEvidence]
    estimated_minutes: Optional[int]
    estimate_method: str
    estimate_confidence: str
    word_count: int
    notes: str
    inspected_at: str
    verification_method: str = "CONTENT_INSPECTION"
    section: Optional[str] = None


COLLECTION_HINTS = (
    "playlist",
    "/tag/",
    "/tags/",
    "/search?",
    "course-catalog",
    "/courses/",
    "curriculum",
    "table-of-contents",
    "/part-",
)


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", html)
    html = re.sub(r"(?is)<nav[^>]*>.*?</nav>", " ", html)
    html = re.sub(r"(?is)<footer[^>]*>.*?</footer>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_url(url: str, timeout: float = 20.0) -> tuple[Optional[int], Optional[str], Optional[str]]:
    """Return (status, text_or_none, error)."""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"},
        ) as client:
            resp = client.get(url)
            ctype = (resp.headers.get("content-type") or "").lower()
            if resp.status_code >= 400:
                return resp.status_code, None, f"HTTP {resp.status_code}"
            if "pdf" in ctype or url.lower().endswith(".pdf"):
                # PDF binary — cannot fully inspect text without parser; mark needs review path
                return resp.status_code, None, "PDF_BINARY_NO_TEXT"
            body = resp.text
            if len(body) < 80:
                return resp.status_code, None, "EMPTY_BODY"
            return resp.status_code, body, None
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)[:200]


def infer_exactness(url: str, title: str, section: Optional[str], text: Optional[str]) -> str:
    u = (url or "").lower()
    t = (title or "").lower()
    if any(h in u for h in COLLECTION_HINTS) or "playlist" in t:
        if section:
            return EXACTNESS_MULTI_TOPIC
        return EXACTNESS_COLLECTION
    if section and ("lecture" in t or "cs50" in u or "youtube.com" in u or "youtu.be" in u):
        return EXACTNESS_MULTI_TOPIC
    # Long hub pages
    if text and len(text.split()) > 6000 and not section:
        return EXACTNESS_MULTI_TOPIC
    return EXACTNESS_EXACT


def estimate_from_text(word_count: int, resource_type: Optional[str], section_minutes: Optional[int]) -> tuple[int, str, str]:
    if section_minutes is not None:
        return int(section_minutes), "VIDEO_SEGMENT_DURATION", "HIGH"
    rt = (resource_type or "").lower()
    if "video" in rt:
        # Unknown full video length — conservative medium fallback
        return 25, "STANDARD_FALLBACK", "LOW"
    # ~200 wpm reading + note buffer
    if word_count <= 0:
        return 20, "STANDARD_FALLBACK", "LOW"
    minutes = max(8, min(90, int(word_count / 180) + 5))
    return minutes, "DOCUMENT_WORD_COUNT_ESTIMATE", "MEDIUM"


def _find_evidence(text_lower: str, terms: list[str]) -> Optional[tuple[str, list[str]]]:
    if not terms:
        return None
    matched = []
    for t in terms:
        # whole-word-ish match to reduce false positives
        if re.search(rf"(?<![a-z0-9]){re.escape(t.lower())}(?![a-z0-9])", text_lower):
            matched.append(t)
    distinctive = [t for t in matched if len(t) >= 5]
    # Require 2 matched terms, or 1 distinctive term length>=6
    if len(matched) >= 2 or (len(distinctive) >= 1 and len(distinctive[0]) >= 6):
        anchor = (distinctive or matched)[0].lower()
        idx = text_lower.find(anchor)
        if idx < 0:
            return None
        start = max(0, idx - 60)
        end = min(len(text_lower), idx + 120)
        snippet = text_lower[start:end].strip()
        return snippet, matched[:6]
    return None


def inspect_resource(
    *,
    resource_slug: str,
    url: str,
    topic_slug: str,
    title: str = "",
    section: Optional[str] = None,
    resource_type: Optional[str] = None,
    known_segment_minutes: Optional[int] = None,
    html_override: Optional[str] = None,
) -> InspectionResult:
    inspected_at = datetime.now(timezone.utc).isoformat()
    concepts = get_topic_concepts(topic_slug)
    required = [c.slug for c in concepts.required] if concepts else []

    if html_override is not None:
        status, html, err = 200, html_override, None
    else:
        status, html, err = fetch_url(url)

    if err == "PDF_BINARY_NO_TEXT":
        return InspectionResult(
            resource_slug=resource_slug,
            url=url,
            accessible=True,
            http_status=status,
            broken=False,
            exactness=EXACTNESS_EXACT if section else EXACTNESS_MULTI_TOPIC,
            verification_status=VERIFICATION_NEEDS_REVIEW,
            covered=[],
            missing=list(required),
            evidence=[],
            estimated_minutes=known_segment_minutes or 30,
            estimate_method="STANDARD_FALLBACK",
            estimate_confidence="LOW",
            word_count=0,
            notes="PDF accessible but text not extracted; cannot claim concept coverage.",
            inspected_at=inspected_at,
            section=section,
        )

    if status is None or (status is not None and status >= 400) or html is None:
        # Bot/WAF 403 on known documentation hosts: not the same as a dead link for learners
        if status == 403:
            return InspectionResult(
                resource_slug=resource_slug,
                url=url,
                accessible=False,
                http_status=status,
                broken=False,
                exactness=infer_exactness(url, title, section, None),
                verification_status=VERIFICATION_NEEDS_REVIEW,
                covered=[],
                missing=list(required),
                evidence=[],
                estimated_minutes=known_segment_minutes or 25,
                estimate_method="STANDARD_FALLBACK",
                estimate_confidence="LOW",
                word_count=0,
                notes="HTTP 403 during automated fetch (possible bot block). URL not marked BROKEN; needs human/browser review.",
                inspected_at=inspected_at,
                section=section,
            )
        return InspectionResult(
            resource_slug=resource_slug,
            url=url,
            accessible=False,
            http_status=status,
            broken=True,
            exactness=EXACTNESS_COLLECTION,
            verification_status=VERIFICATION_BROKEN,
            covered=[],
            missing=list(required),
            evidence=[],
            estimated_minutes=None,
            estimate_method="STANDARD_FALLBACK",
            estimate_confidence="LOW",
            word_count=0,
            notes=f"Broken or inaccessible: {err or status}",
            inspected_at=inspected_at,
            section=section,
        )

    text = _strip_html(html)
    text_lower = text.lower()
    word_count = len(text.split())

    # Paywall heuristics
    paywall_markers = ("subscribe to continue", "sign in to read", "members only", "paywall")
    if any(m in text_lower for m in paywall_markers) and word_count < 400:
        return InspectionResult(
            resource_slug=resource_slug,
            url=url,
            accessible=False,
            http_status=status,
            broken=False,
            exactness=EXACTNESS_COLLECTION,
            verification_status=VERIFICATION_NEEDS_REVIEW,
            covered=[],
            missing=list(required),
            evidence=[],
            estimated_minutes=None,
            estimate_method="STANDARD_FALLBACK",
            estimate_confidence="LOW",
            word_count=word_count,
            notes="Possible paywall / gated content; insufficient accessible text.",
            inspected_at=inspected_at,
            section=section,
        )

    covered: list[str] = []
    evidence: list[ConceptEvidence] = []
    missing: list[str] = []
    for cslug in required:
        terms = get_evidence_terms(topic_slug, cslug)
        hit = _find_evidence(text_lower, terms)
        if hit:
            snippet, matched = hit
            covered.append(cslug)
            evidence.append(ConceptEvidence(concept=cslug, evidence=snippet[:200], matched_terms=matched))
        else:
            missing.append(cslug)

    exactness = infer_exactness(url, title, section, text)
    minutes, method, confidence = estimate_from_text(word_count, resource_type, known_segment_minutes)

    if exactness == EXACTNESS_COLLECTION and not section:
        vstatus = VERIFICATION_COLLECTION_ONLY
        notes = "Collection/hub without exact section; cannot be EXACT PRIMARY alone."
    elif not required:
        vstatus = VERIFICATION_NEEDS_REVIEW
        notes = "No concept contract; refuse coverage claim."
    elif not covered:
        vstatus = VERIFICATION_NEEDS_REVIEW
        notes = "Accessible but no required-concept evidence found in text."
    elif missing:
        vstatus = VERIFICATION_PARTIAL_COVERAGE
        notes = f"Partial coverage; missing={missing}"
    else:
        vstatus = VERIFICATION_VERIFIED_COVERAGE
        notes = "All required concepts have independent text evidence."

    # MULTI_TOPIC without section cannot be treated as clean EXACT ready alone
    if exactness == EXACTNESS_MULTI_TOPIC and not section and vstatus == VERIFICATION_VERIFIED_COVERAGE:
        notes = (notes or "") + " MULTI_TOPIC without section — demote confidence."
        # Keep coverage but flag needs precise navigation
        if "youtube" in url.lower() or "lecture" in (title or "").lower():
            vstatus = VERIFICATION_NEEDS_REVIEW
            notes = "Multi-topic video/lecture without timestamp/section."

    return InspectionResult(
        resource_slug=resource_slug,
        url=url,
        accessible=True,
        http_status=status,
        broken=False,
        exactness=exactness,
        verification_status=vstatus,
        covered=covered,
        missing=missing,
        evidence=evidence,
        estimated_minutes=minutes,
        estimate_method=method,
        estimate_confidence=confidence,
        word_count=word_count,
        notes=notes,
        inspected_at=inspected_at,
        section=section,
    )


def inspect_with_retries(url: str, **kwargs) -> InspectionResult:
    result = inspect_resource(url=url, **kwargs)
    if result.broken and result.http_status is None:
        time.sleep(0.4)
        result = inspect_resource(url=url, **kwargs)
    return result
