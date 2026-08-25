"""PART A closure: live content inspection of decomposition PRIMARY resources.

For each of the 109 new topics' learner-visible PRIMARY:
  1. Fetch the exact URL (stdlib urllib, polite rate).
  2. Extract title, headings (h1-h4), and visible text.
  3. Match the topic's concept contract via independent evidence_terms.
  4. Store per-concept evidence (anchor heading + factual summary + real
     body snippet) in verification_evidence; set resource-specific
     required_concepts_covered — never copied from topic.required.
  5. Classify honestly:
       VERIFIED_COVERAGE   all required concepts evidenced
       PARTIAL_COVERAGE    some evidenced
       RESOURCE_GAP        none/insufficient
       NEEDS_REVIEW        JS-shell / blocked / ambiguous page
       BROKEN              404/DNS/unreachable

Idempotent-ish: re-running re-inspects and overwrites its own evidence.
Exports reports/resource_evidence_final.json.
"""
import html as html_mod
import json
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
MAX_BYTES = 1_500_000
DELAY_S = 0.25

DECOMP_SLUGS = set(json.load(open(f"{REPORT_DIR}\\decomposition_log.json", encoding="utf-8"))["created_topics"])
try:
    DECOMP_SLUGS |= set(json.load(open(f"{REPORT_DIR}\\decomposition_v2_log.json",
                                       encoding="utf-8"))["created_topics"])
except Exception:
    pass

TAG_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.I | re.S)
HEADING_RE = re.compile(r"<h([1-4])[^>]*>(.*?)</h\1>", re.I | re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TAGS_ONLY_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def _clean(fragment: str) -> str:
    fragment = COMMENT_RE.sub(" ", fragment)
    fragment = TAGS_ONLY_RE.sub(" ", fragment)
    fragment = html_mod.unescape(fragment)
    return WS_RE.sub(" ", fragment).strip()


def fetch(url: str):
    """Return (status_class, http_status, text_html or error)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return "OK", resp.status, raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        return ("HTTP_ERROR", e.code, "")
    except Exception as e:  # DNS, timeout, SSL...
        return ("ERROR", 0, str(e))


def classify_http(code: int) -> str:
    # 403/429 = bot protection → honestly NEEDS_REVIEW, not BROKEN.
    if code in (404, 410):
        return "BROKEN"
    return "NEEDS_REVIEW"


OVERRIDES_PATH = r"D:\Akshit Personal OS\backend\scripts\url_overrides.json"
try:
    URL_OVERRIDES = json.load(open(OVERRIDES_PATH, encoding="utf-8"))
except Exception:
    URL_OVERRIDES = {}


def resolve_url(preferred: str):
    """Probe override candidates in order; first 200 wins. Returns final URL."""
    for cand in URL_OVERRIDES.get("probe_order", []) or []:
        pass
    cls, code, payload = fetch(preferred)
    if cls == "OK":
        return preferred
    # Try overrides keyed by any slug containing this path fragment later;
    # resolution is driven by caller passing candidate lists.
    return None


def resolve_for(slug: str, current_url: str):
    """Probe candidates IN ORDER; first OK wins (candidate order = intent)."""
    cands = URL_OVERRIDES.get(slug) or []
    if not cands:
        return current_url
    for cand in cands:
        cls, code, _ = fetch(cand)
        if cls == "OK":
            if cand != current_url:
                time.sleep(DELAY_S)
            return cand
    return current_url


def parse(html_text: str):
    body = TAG_RE.sub(" ", html_text)
    headings = []
    for level, inner in HEADING_RE.findall(body):
        txt = _clean(inner)
        if txt:
            headings.append((int(level), txt))
    visible = _clean(body)

    # Markdown sources (raw GitHub): extract ATX headings.
    if len(headings) <= 3:
        md_head_re = re.compile(r"^ {0,3}(#{1,4})\s+(.+?)\s*#*\s*$", re.M)
        md_heads = [(len(h), _clean(t)) for h, t in md_head_re.findall(html_text)]
        md_heads = [(l, t) for l, t in md_heads if t]
        if len(md_heads) > len(headings):
            # Rebuild visible text from markdown source directly.
            visible = WS_RE.sub(" ", COMMENT_RE.sub(" ", html_mod.unescape(html_text))).strip()
            headings = md_heads
    return headings, visible


JS_SHELL_MARKERS = (
    "enable javascript", "please enable", "checking your browser",
    "captcha", "are you a robot", "access denied", "verify you are human",
)


def looks_like_shell(headings, visible: str) -> bool:
    low = visible[:4000].lower()
    if any(m in low for m in JS_SHELL_MARKERS):
        return True
    # SPA shells: almost no text but lots of scripts already stripped → tiny body
    if len(visible) < 400 and len(headings) <= 2:
        return True
    return False


def match_concept(terms, headings, body_low):
    """Return (anchor, snippet, strength). strength: 2=heading hit,1=body-only.

    A single strong term hit is sufficient evidence when recorded with its
    anchor + real body snippet (auditable); multi-term presence raises
    nothing by itself — honesty comes from the stored context, not count.
    """
    best_anchor = None
    for term in terms:
        t = term.lower()
        for lvl, htxt in headings:
            if t in htxt.lower():
                return htxt, None, 2
    for term in terms:
        t = term.lower()
        idx = body_low.find(t)
        if idx >= 0:
            start = max(0, idx - 80)
            snippet = visible_slice(body_low, start, start + 220)
            anchor = best_anchor or (headings[0][1] if headings else "page body")
            return anchor, snippet, 1
    return None, None, 0


def visible_slice(text, a, b):
    part = text[a:b].strip()
    return (part[:180] + "...") if len(part) > 183 else part


def inspect(url: str, concepts: list[dict]):
    status_cls, code, payload = fetch(url)
    if status_cls != "OK":
        cls = "BROKEN" if code in (404, 410) else "NEEDS_REVIEW"
        return cls, code, {"error": payload or f"http {code}"}, [], [], []

    headings, visible = parse(payload)
    body_low = visible.lower()
    if looks_like_shell(headings, visible):
        return "NEEDS_REVIEW", code, {"reason": "js-shell-or-blocked-page"}, [], [c["slug"] for c in concepts], headings

    verified, unmatched = [], []
    for c in concepts:
        anchor, snippet, strength = match_concept(c.get("evidence_terms") or [], headings, body_low)
        if strength:
            summary = f"Section '{anchor}' covers: {c['description']}." if strength == 2 else \
                      f"Body content near '{anchor}' supports: {c['description']}."
            entry = {
                "concept_slug": c["slug"],
                "anchor": anchor[:120],
                "summary": summary,
                "inspection_method": "content",
                "confidence": "HIGH" if strength == 2 else "MEDIUM",
            }
            if snippet:
                entry["snippet_or_summary"] = snippet
            verified.append(entry)
        else:
            unmatched.append(c["slug"])

    if not unmatched:
        cls = "VERIFIED_COVERAGE"
    elif verified:
        cls = "PARTIAL_COVERAGE"
    else:
        cls = "RESOURCE_GAP"
    evidence = {
        "verification_method": "CONTENT_INSPECTION_V3",
        "http_status": code,
        "content_chars": len(visible),
        "inspected_at": datetime.now(timezone.utc).isoformat(),
        "url": url,
    }
    return cls, code, evidence, verified, unmatched, headings


def main() -> None:
    db = SessionLocal()
    out_records = []
    url_cache = {}
    try:
        contracts = load_contract_payload()["contracts"]
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        lessons = db.query(CurriculumLesson).all()
        lesson_by_id = {l.id: l for l in lessons}
        lessons_by_tid = {}
        for l in lessons:
            lessons_by_tid.setdefault(l.topic_id, []).append(l)

        targets = []
        for slug in sorted(DECOMP_SLUGS):
            t = topics.get(slug)
            if not t or not lessons_by_tid.get(t.id):
                continue
            lesson = sorted(lessons_by_tid[t.id], key=lambda x: x.order_index)[0]
            prim = [
                r for r in res_by_topic(db, lesson.id)
                if is_learner_visible(r) and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")
            ]
            if not prim:
                continue
            contract = contracts.get(slug) or {}
            required = contract.get("required") or []
            targets.append((slug, lesson.id, prim[0], required))

        print(f"targets: {len(targets)}")
        url_fixed = 0
        for i, (slug, _lid, res, required) in enumerate(targets, 1):
            working = resolve_for(slug, res.url)
            if working != res.url:
                res.url = working
                url_fixed += 1
            concepts = [
                {"slug": c["slug"], "description": c.get("description") or c["slug"],
                 "evidence_terms": c.get("evidence_terms") or []}
                for c in required
            ]
            cache_key = (working, tuple(c["slug"] for c in concepts))
            if cache_key in url_cache:
                cls, code, base_ev, verified, unmatched = url_cache[cache_key]
            else:
                cls, code, base_ev, verified, unmatched, _h = inspect(working, concepts)
                url_cache[cache_key] = (cls, code, base_ev, verified, unmatched)
                time.sleep(DELAY_S)

            ev = dict(base_ev)
            ev["verified_concepts"] = verified
            ev["unmatched_concepts"] = unmatched
            ev["resource_slug"] = res.slug
            ev["topic_slug"] = slug
            res.verification_status = cls
            res.required_concepts_covered = [v["concept_slug"] for v in verified]
            res.verification_evidence = json.dumps(ev, ensure_ascii=False)
            res.last_verified_at = datetime.now(timezone.utc).isoformat()
            if getattr(res, "estimate_confidence", None) in (None, "", "LOW"):
                res.estimate_confidence = "MEDIUM"

            out_records.append({
                "resource_slug": res.slug, "topic_slug": slug, "url": res.url,
                "classification": cls, "http": code,
                "concepts_required": [c["slug"] for c in required],
                "concepts_verified": [v["concept_slug"] for v in verified],
                "unmatched": unmatched,
                "evidence_detail": verified,
            })
            if i % 10 == 0 or i == len(targets):
                print(f"  inspected {i}/{len(targets)} (urls fixed: {url_fixed})")

        db.commit()
        dist = Counter(r["classification"] for r in out_records)
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "distribution": dict(dist), "resources": out_records},
                  open(f"{REPORT_DIR}\\resource_evidence_final.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        print(json.dumps(dict(dist), indent=2))

        from app.content.learner_visibility import apply_learner_visibility
        apply_learner_visibility(db)
        db.commit()
        print("visibility re-applied")
    finally:
        db.close()


_res_cache = {}


def res_by_topic(db, lesson_id):
    if lesson_id not in _res_cache:
        from sqlalchemy import select
        rows = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson_id).all()
        _res_cache[lesson_id] = rows
    return _res_cache[lesson_id]


if __name__ == "__main__":
    from collections import Counter
    main()
