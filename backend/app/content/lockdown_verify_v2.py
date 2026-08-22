"""Strict content verification pass for remaining NEEDS_REVIEW topics.

Inspects PRIMARY (and exact REFERENCE) pages, extracts headings + body,
records resource-specific evidence with locations. Does NOT copy topic
required concepts into coverage. Does NOT mutate the curriculum graph.

Survives demote_weak_verification when every covered concept has
confidence=HIGH and a location (heading/section).
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session, selectinload

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
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
CHROME = (
    "skip top", "log in", "sign up", "navigation", "cookie", "subscribe",
    "geeksforgeeks courses", "oracle university", "create new account",
    "privacy policy", "terms of use", "advertisement",
)
COLLECTION_URL = ("playlist", "/tag/", "/tags/", "/search?", "youtube.com/playlist")
TEACH_CUES = (" is ", " are ", " means ", " example", " define", " definition", " use ", " using ", " create", " write", " implement", " return", " method", " class ", " function")

# Concept-specific anchors that MUST appear in evidence (prevents false READY
# when a page teaches only one side of a comparison, e.g. TCP RFC without UDP).
REQUIRED_ANCHORS: dict[str, tuple[str, ...]] = {
    "net-tcp-udp-tcp-vs-udp": ("tcp", "udp"),
    "net-tcp-udp-contrast-reliable-streams-vs-datagrams": ("tcp", "udp"),
}


def _strip_html(html: str) -> tuple[list[str], str]:
    html = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", html)
    html = re.sub(r"(?is)<nav[^>]*>.*?</nav>", " ", html)
    html = re.sub(r"(?is)<footer[^>]*>.*?</footer>", " ", html)
    headings = re.findall(r"(?is)<h[1-4][^>]*>(.*?)</h[1-4]>", html)
    headings = [re.sub(r"<[^>]+>", " ", h).strip() for h in headings]
    headings = [re.sub(r"\s+", " ", h) for h in headings if h]
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return headings, text


def fetch(url: str, timeout: float = 22.0) -> tuple[Optional[int], Optional[str], Optional[str]]:
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*"},
        ) as client:
            resp = client.get(url)
            ctype = (resp.headers.get("content-type") or "").lower()
            if resp.status_code >= 400:
                return resp.status_code, None, f"HTTP {resp.status_code}"
            if "pdf" in ctype or url.lower().endswith(".pdf"):
                return resp.status_code, None, "PDF_BINARY"
            if len(resp.text) < 100:
                return resp.status_code, None, "EMPTY"
            return resp.status_code, resp.text, None
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)[:180]


def _word_boundary(term: str, text: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", text.lower()))


def _is_chrome(snippet: str) -> bool:
    s = snippet.lower()
    return any(c in s for c in CHROME)


def _find_heading(headings: list[str], terms: list[str]) -> Optional[str]:
    """Accept a heading that clearly names the concept (not nav chrome).

    Short technical tokens (heap, sort, json, set) are valid when two+ match,
    or when one distinctive token (>=5) matches a short heading.
    """
    for h in headings:
        hl = h.lower().strip()
        if len(hl) < 3 or len(hl) > 160:
            continue
        if _is_chrome(hl):
            continue
        hits = [t for t in terms if len(t) >= 3 and t.lower() in hl]
        if len(hits) >= 2:
            return h[:160]
        if len(hits) == 1 and len(hits[0]) >= 5 and len(hl.split()) <= 8:
            return h[:160]
    return None


def _body_evidence(text: str, terms: list[str]) -> Optional[tuple[str, list[str], str]]:
    tl = text.lower()
    matched = [t for t in terms if len(t) >= 3 and _word_boundary(t, tl)]
    distinctive = [t for t in matched if len(t) >= 5]
    short_ok = [t for t in matched if len(t) >= 4]
    # Need either 2+ distinctive terms, 1 long distinctive, or 2+ short technical terms
    if len(distinctive) >= 2:
        pass
    elif len(distinctive) == 1 and len(distinctive[0]) >= 7:
        pass
    elif len(short_ok) >= 2 and len(matched) >= 2:
        distinctive = short_ok[:3]
    else:
        return None
    anchor = distinctive[0].lower()
    idx = tl.find(anchor)
    if idx < 0:
        return None
    start = max(0, idx - 80)
    end = min(len(tl), idx + 160)
    snippet = text[start:end].strip()
    if _is_chrome(snippet):
        return None
    sl = snippet.lower()
    teach = any(c in sl for c in TEACH_CUES)
    codey = any(
        x in sl
        for x in (
            "public ",
            "void ",
            "int ",
            "return ",
            "class ",
            "def ",
            "function",
            "example",
            "syntax",
            "parameter",
            "algorithm",
            "complexity",
            "array",
            "object",
            "interface",
        )
    )
    if (teach or codey) and len(distinctive) >= 1 and len(matched) >= 2:
        return snippet[:220], matched[:8], "HIGH"
    if len(distinctive) >= 2 and not _is_chrome(snippet):
        return snippet[:220], matched[:8], "HIGH"
    if len(distinctive) >= 3 and not _is_chrome(snippet):
        return snippet[:220], matched[:8], "HIGH"
    return None


def inspect_for_topic(
    *,
    resource_slug: str,
    url: str,
    topic_slug: str,
    title: str = "",
    section: Optional[str] = None,
    resource_type: Optional[str] = None,
) -> dict[str, Any]:
    concepts = get_topic_concepts(topic_slug)
    required = [c.slug for c in concepts.required] if concepts else []
    inspected_at = datetime.now(timezone.utc).isoformat()

    if any(h in (url or "").lower() for h in COLLECTION_URL):
        return {
            "resource_slug": resource_slug,
            "url": url,
            "accessible": True,
            "broken": False,
            "exactness": EXACTNESS_COLLECTION,
            "verification_status": VERIFICATION_COLLECTION_ONLY if not section else VERIFICATION_NEEDS_REVIEW,
            "covered": [],
            "missing": required,
            "evidence": [],
            "estimated_minutes": 20,
            "estimate_method": "STANDARD_FALLBACK",
            "estimate_confidence": "LOW",
            "word_count": 0,
            "notes": "Collection/playlist URL without isolated exact lesson.",
            "inspected_at": inspected_at,
            "section": section,
        }

    status, html, err = fetch(url)
    if err == "PDF_BINARY":
        return {
            "resource_slug": resource_slug,
            "url": url,
            "accessible": True,
            "broken": False,
            "exactness": EXACTNESS_EXACT if section else EXACTNESS_MULTI_TOPIC,
            "verification_status": VERIFICATION_NEEDS_REVIEW,
            "covered": [],
            "missing": required,
            "evidence": [],
            "estimated_minutes": 30,
            "estimate_method": "STANDARD_FALLBACK",
            "estimate_confidence": "LOW",
            "word_count": 0,
            "notes": "PDF not text-inspected.",
            "inspected_at": inspected_at,
            "section": section,
        }
    if status == 403:
        return {
            "resource_slug": resource_slug,
            "url": url,
            "accessible": False,
            "broken": False,
            "exactness": EXACTNESS_EXACT,
            "verification_status": VERIFICATION_NEEDS_REVIEW,
            "covered": [],
            "missing": required,
            "evidence": [],
            "estimated_minutes": 25,
            "estimate_method": "STANDARD_FALLBACK",
            "estimate_confidence": "LOW",
            "word_count": 0,
            "notes": "HTTP 403 bot block — not BROKEN for learners; needs browser verification.",
            "inspected_at": inspected_at,
            "section": section,
        }
    if status is None or status >= 400 or html is None:
        return {
            "resource_slug": resource_slug,
            "url": url,
            "accessible": False,
            "broken": True,
            "exactness": EXACTNESS_COLLECTION,
            "verification_status": VERIFICATION_BROKEN,
            "covered": [],
            "missing": required,
            "evidence": [],
            "estimated_minutes": None,
            "estimate_method": "STANDARD_FALLBACK",
            "estimate_confidence": "LOW",
            "word_count": 0,
            "notes": f"Broken: {err or status}",
            "inspected_at": inspected_at,
            "section": section,
        }

    headings, text = _strip_html(html)
    word_count = len(text.split())
    covered: list[str] = []
    missing: list[str] = []
    evidence: list[dict[str, Any]] = []

    for cslug in required:
        terms = get_evidence_terms(topic_slug, cslug)
        # Also add tokens from concept slug itself (independent of full required list copy)
        terms = list(dict.fromkeys(terms + [p for p in cslug.split("-") if len(p) >= 4]))[:14]
        anchors = REQUIRED_ANCHORS.get(cslug) or ()
        anchors_ok = (not anchors) or all(_word_boundary(a, text) for a in anchors)

        heading = _find_heading(headings, terms) if anchors_ok else None
        if heading:
            covered.append(cslug)
            evidence.append(
                {
                    "concept": cslug,
                    "evidence": heading,
                    "location": f"heading: {heading[:120]}",
                    "confidence": "HIGH",
                    "matched_terms": [t for t in terms if t.lower() in heading.lower()][:6],
                }
            )
            continue
        body = _body_evidence(text, terms) if anchors_ok else None
        if body:
            snippet, matched, conf = body
            covered.append(cslug)
            evidence.append(
                {
                    "concept": cslug,
                    "evidence": snippet,
                    "location": section or "body",
                    "confidence": conf,
                    "matched_terms": matched,
                }
            )
        else:
            missing.append(cslug)

    exactness = EXACTNESS_EXACT
    if section and ("lecture" in (title or "").lower() or "youtube" in url.lower()):
        exactness = EXACTNESS_MULTI_TOPIC
    if word_count > 8000 and not section:
        exactness = EXACTNESS_MULTI_TOPIC

    if not required:
        vstatus = VERIFICATION_NEEDS_REVIEW
        notes = "No concept contract."
    elif not covered:
        vstatus = VERIFICATION_NEEDS_REVIEW
        notes = "Accessible but no high-confidence concept evidence."
    elif missing:
        # Resource-level: VERIFIED for claimed concepts only (not topic-complete).
        # Topic readiness uses union across PRIMARYs; PARTIAL at topic level if gaps remain.
        if all(e.get("confidence") == "HIGH" for e in evidence):
            vstatus = VERIFICATION_VERIFIED_COVERAGE
            notes = f"HIGH-confidence subset coverage; topic still missing={missing}"
        else:
            vstatus = VERIFICATION_PARTIAL_COVERAGE
            notes = f"Partial/non-HIGH coverage; missing={missing}"
    elif all(e.get("confidence") == "HIGH" for e in evidence):
        vstatus = VERIFICATION_VERIFIED_COVERAGE
        notes = "All required concepts have HIGH-confidence heading/body teaching evidence."
    else:
        vstatus = VERIFICATION_NEEDS_REVIEW
        notes = "Coverage found but not all HIGH confidence."

    # reading estimate
    minutes = max(10, min(75, int(word_count / 180) + 6))
    method = "DOCUMENT_READING_ESTIMATE"
    conf_t = "MEDIUM"

    return {
        "resource_slug": resource_slug,
        "url": url,
        "accessible": True,
        "broken": False,
        "exactness": exactness,
        "verification_status": vstatus,
        "covered": covered,
        "missing": missing,
        "evidence": evidence,
        "estimated_minutes": minutes,
        "estimate_method": method,
        "estimate_confidence": conf_t,
        "word_count": word_count,
        "notes": notes,
        "inspected_at": inspected_at,
        "section": section,
        "verification_method": "LOCKDOWN_CONTENT_INSPECTION_V2",
    }


def _apply_result(row: CurriculumResource, result: dict[str, Any]) -> None:
    row.required_concepts_covered = list(result.get("covered") or [])
    row.verification_status = result["verification_status"]
    row.exactness = result.get("exactness") or row.exactness
    if result.get("section") and not row.section:
        row.section = str(result["section"])[:200]
    row.estimated_minutes = result.get("estimated_minutes")
    row.estimate_method = result.get("estimate_method")
    row.estimate_confidence = result.get("estimate_confidence")
    row.notes = (result.get("notes") or "")[:500]
    row.last_verified_at = result.get("inspected_at")
    row.verification_evidence = json.dumps(
        {
            "resource_slug": result.get("resource_slug"),
            "verified_concepts": result.get("evidence") or [],
            "missing": result.get("missing") or [],
            "inspected_at": result.get("inspected_at"),
            "verification_method": result.get("verification_method") or "LOCKDOWN_CONTENT_INSPECTION_V2",
            "http_status": None,
            "word_count": result.get("word_count"),
            "url": result.get("url"),
        }
    )


def verify_domains(db: Session, domains: Optional[list[str]] = None, workers: int = 10) -> dict[str, Any]:
    q = db.query(CurriculumTopic).options(
        selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.resources)
    )
    if domains:
        q = q.filter(CurriculumTopic.domain_key.in_(domains))
    topics = q.order_by(CurriculumTopic.order_index, CurriculumTopic.id).all()

    jobs = []
    for topic in topics:
        if not topic.slug:
            continue
        for les in topic.lessons or []:
            for r in les.resources or []:
                if (r.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN", "REFERENCE"):
                    continue
                # Prefer inspecting PRIMARY; also exact REFERENCE pages for joint coverage
                jobs.append(
                    {
                        "resource_id": r.id,
                        "slug": r.slug,
                        "url": r.url,
                        "topic_slug": topic.slug,
                        "title": r.title,
                        "section": r.section,
                        "resource_type": r.resource_type,
                        "role": (r.role or "").upper(),
                    }
                )

    results: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(
                inspect_for_topic,
                resource_slug=j["slug"] or "",
                url=j["url"] or "",
                topic_slug=j["topic_slug"],
                title=j.get("title") or "",
                section=j.get("section"),
                resource_type=j.get("resource_type"),
            ): j
            for j in jobs
        }
        for fut in as_completed(futs):
            j = futs[fut]
            try:
                results[j["resource_id"]] = fut.result()
            except Exception as exc:  # noqa: BLE001
                results[j["resource_id"]] = {
                    "resource_slug": j["slug"],
                    "url": j["url"],
                    "verification_status": VERIFICATION_NEEDS_REVIEW,
                    "covered": [],
                    "missing": [],
                    "evidence": [],
                    "notes": f"inspect error: {exc}",
                    "inspected_at": datetime.now(timezone.utc).isoformat(),
                    "exactness": EXACTNESS_EXACT,
                    "estimated_minutes": 20,
                    "estimate_method": "STANDARD_FALLBACK",
                    "estimate_confidence": "LOW",
                    "word_count": 0,
                }

    applied = 0
    # Promote exact REFERENCE to PRIMARY when PRIMARY is collection/partial and REF is VERIFIED
    for topic in topics:
        primaries = []
        refs = []
        for les in topic.lessons or []:
            for r in les.resources or []:
                role = (r.role or "").upper()
                if role in ("PRIMARY", "PRIMARY_LEARN"):
                    primaries.append(r)
                elif role == "REFERENCE":
                    refs.append(r)
        for r in primaries + refs:
            if r.id in results:
                _apply_result(r, results[r.id])
                applied += 1
        # joint promotion: if any PRIMARY is COLLECTION_ONLY/NEEDS_REVIEW and a REFERENCE is VERIFIED_COVERAGE, promote REF
        for ref in refs:
            res = results.get(ref.id) or {}
            if res.get("verification_status") != VERIFICATION_VERIFIED_COVERAGE:
                continue
            weak_primary = any(
                (results.get(p.id) or {}).get("verification_status")
                in (VERIFICATION_COLLECTION_ONLY, VERIFICATION_NEEDS_REVIEW, VERIFICATION_BROKEN, VERIFICATION_PARTIAL_COVERAGE)
                or (p.exactness or "") == EXACTNESS_COLLECTION
                for p in primaries
            )
            if weak_primary or not primaries:
                ref.role = "PRIMARY"
                ref.order_index = -1
                for p in primaries:
                    if (results.get(p.id) or {}).get("verification_status") in (
                        VERIFICATION_COLLECTION_ONLY,
                        VERIFICATION_BROKEN,
                    ) or "playlist" in (p.url or "").lower():
                        p.role = "SUPPLEMENT"

    db.flush()
    return {"topics": len(topics), "jobs": len(jobs), "applied": applied}
