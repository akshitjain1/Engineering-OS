"""Check every mapped resource URL against the live internet.

The curriculum's whole promise is "open exactly this page and study it". That
promise is only as good as the URLs, and nothing here had ever fetched one.
This script does, and reports the four ways a mapping can quietly be wrong:

DEAD             the server answered, and said the page is not there (4xx/5xx)
UNREACHABLE      no answer at all: timeout, DNS or TLS failure. Ambiguous --
                 the page may be fine and the network in the way, so this is
                 reported separately and never treated as a broken mapping
PLAIN_TEXT       it loads but the browser shows source, not a rendered page
                 (raw.githubusercontent.com markdown: unrendered LaTeX)
REDIRECTED       the URL still resolves but lands somewhere else now
PROVIDER_MISMATCH the recorded provider is not the host actually serving it

Run:
    python -m app.content.audit_resource_links               # audit only
    python -m app.content.audit_resource_links --limit 50    # quick sample
    python -m app.content.audit_resource_links --record      # also stamp evidence

``--record`` writes what was observed back onto each resource row:
``last_verified_at`` and a ``verification_evidence`` entry holding the HTTP
status, the URL finally landed on and the page title read from it.

That is deliberately a *narrower* claim than ``verification_status``. This
script establishes that a URL is live and which page it serves. It does not and
cannot establish that the page covers the topic's required concepts, which is
what ``VERIFIED_COVERAGE`` asserts. Those two facts are recorded separately, and
this one never edits the other -- a link check is not a content review.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import urllib.error
import urllib.request
from datetime import datetime, timezone

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

#: provider name (lowercased) -> substring that must appear in the URL host.
PROVIDER_HOSTS: dict[str, tuple[str, ...]] = {
    "opencv": ("opencv.org",),
    "pytorch": ("pytorch.org",),
    "tensorflow": ("tensorflow.org",),
    "d2l.ai": ("d2l.ai",),
    "dive into deep learning": ("d2l.ai",),
    "scikit-learn": ("scikit-learn.org",),
    "scikit-image": ("scikit-image.org",),
    "stanford cs231n": ("cs231n.github.io", "stanford.edu"),
    "stanford cs229": ("cs229.stanford.edu", "stanford.edu"),
    "ultralytics": ("ultralytics.com",),
    "numpy": ("numpy.org",),
    "pandas": ("pandas.pydata.org",),
    "matplotlib": ("matplotlib.org",),
    "hugging face": ("huggingface.co",),
    "huggingface": ("huggingface.co",),
    "geeksforgeeks": ("geeksforgeeks.org",),
    "w3schools": ("w3schools.com",),
    "leetcode": ("leetcode.com",),
    "neetcode": ("neetcode.io",),
    "mit opencourseware": ("mit.edu",),
    "fastapi": ("fastapi.tiangolo.com",),
    "docker": ("docker.com", "docs.docker.com"),
    "kubernetes": ("kubernetes.io",),
    "mlflow": ("mlflow.org",),
    "python": ("python.org",),
    "postgresql": ("postgresql.org",),
    "redis": ("redis.io",),
    "git": ("git-scm.com",),
    "github": ("github.com", "docs.github.com"),
    "cs50x": ("cs50.harvard.edu", "harvard.edu"),
    "harvard cs50": ("cs50.harvard.edu", "harvard.edu"),
    "vizuara": ("youtube.com", "youtu.be"),
    "3blue1brown": ("3blue1brown.com", "youtube.com", "youtu.be"),
    "khan academy": ("khanacademy.org",),
    "openai": ("openai.com",),
    "langchain": ("langchain.com", "python.langchain.com"),
    "weights & biases": ("wandb.ai",),
    "arxiv": ("arxiv.org",),
    "real python": ("realpython.com",),
    "astral": ("astral.sh", "docs.astral.sh"),
    # Anthropic's developer documentation is served from platform.claude.com.
    "anthropic": ("anthropic.com", "platform.claude.com", "docs.claude.com"),
    "oracle": ("oracle.com",),
    "pinecone": ("pinecone.io",),
    "mit missing semester": ("missing.csail.mit.edu",),
    "gnu": ("gnu.org",),
    "visual studio code": ("code.visualstudio.com",),
    "junit": ("junit.org", "docs.junit.org"),
    "python packaging": ("packaging.python.org",),
}

_TITLE = re.compile(rb"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass
class LinkCheck:
    url: str
    status: Optional[int] = None
    final_url: Optional[str] = None
    content_type: Optional[str] = None
    page_title: Optional[str] = None
    error: Optional[str] = None
    flags: list[str] = field(default_factory=list)


def fetch(url: str, timeout: int = 25) -> LinkCheck:
    check = LinkCheck(url=url)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            check.status = response.status
            check.final_url = response.geturl()
            check.content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip()
            head = response.read(60_000)
        match = _TITLE.search(head)
        if match:
            title = match.group(1).decode("utf-8", "replace")
            check.page_title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title)).strip()[:200]
    except urllib.error.HTTPError as exc:
        check.status = exc.code
        check.error = f"HTTP {exc.code}"
    except Exception as exc:  # timeouts, DNS, TLS, redirect loops
        check.error = f"{type(exc).__name__}: {exc}"[:160]
    return check


#: Hosts that answer 403 to anything without a real browser session. A 403
#: from these is bot protection, not a missing page.
BOT_PROTECTED = ("leetcode.com", "mlflow.org", "medium.com", "codeforces.com")


def classify(check: LinkCheck, provider: Optional[str]) -> list[str]:
    flags: list[str] = []
    host = urlparse(check.final_url or check.url).netloc.lower()

    if check.status is None:
        # No HTTP response at all. Could be the page, could be the network.
        flags.append("UNREACHABLE")
        return flags
    if check.status == 403 and any(token in host for token in BOT_PROTECTED):
        flags.append("BOT_PROTECTED")
        return flags
    if check.status >= 400:
        flags.append("DEAD")
        return flags
    if check.status >= 300:
        # Answered with a redirect this client could not complete.
        flags.append("UNREACHABLE")
        return flags

    if check.content_type == "text/plain" or "raw.githubusercontent.com" in host:
        # A browser shows this as source. LaTeX, directives and figures do not
        # render, so it cannot be read as a lesson.
        flags.append("PLAIN_TEXT")

    if check.final_url and check.final_url.rstrip("/") != check.url.rstrip("/"):
        before = urlparse(check.url)
        after = urlparse(check.final_url)
        if before.netloc != after.netloc or before.path.rstrip("/") != after.path.rstrip("/"):
            flags.append("REDIRECTED")

    key = (provider or "").strip().lower()
    expected = PROVIDER_HOSTS.get(key)
    if expected and not any(token in host for token in expected):
        flags.append("PROVIDER_MISMATCH")

    return flags


def record_evidence(db_path: Path, checks: dict[str, LinkCheck]) -> int:
    """Stamp the observed link facts onto every resource row that was checked.

    Only touches ``last_verified_at`` and ``verification_evidence``.
    ``verification_status`` is left exactly as it was: whether a page covers the
    concepts a topic requires is a judgement a fetch cannot make.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    stamped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated = 0

    rows = conn.execute(
        "SELECT id, url, verification_evidence FROM curriculum_resources "
        "WHERE url IS NOT NULL AND url != ''"
    ).fetchall()

    for row in rows:
        check = checks.get(row["url"])
        if check is None:
            continue
        try:
            evidence = json.loads(row["verification_evidence"] or "{}")
            if not isinstance(evidence, dict):
                evidence = {"prior": evidence}
        except (TypeError, ValueError):
            evidence = {}

        evidence["link_check"] = {
            "checked_at": stamped_at,
            "http_status": check.status,
            "landed_on": check.final_url,
            "content_type": check.content_type,
            "page_title": check.page_title,
            "error": check.error,
            "note": "URL liveness and page identity only; not concept coverage",
        }
        conn.execute(
            "UPDATE curriculum_resources SET verification_evidence = ?, last_verified_at = ? WHERE id = ?",
            (json.dumps(evidence), stamped_at, row["id"]),
        )
        updated += 1

    conn.commit()
    conn.close()
    return updated


def load_resources(db_path: Path, limit: Optional[int] = None) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT r.id, r.title, r.url, r.provider, r.role, r.verification_status,
               r.section, r.exactness, t.slug AS topic_slug, t.name AS topic_name,
               m.slug AS module_slug, s.name AS subject_name
        FROM curriculum_resources r
        LEFT JOIN curriculum_lessons l ON r.lesson_id = l.id
        LEFT JOIN curriculum_topics t ON l.topic_id = t.id
        LEFT JOIN curriculum_modules m ON t.module_id = m.id
        LEFT JOIN curriculum_subjects s ON m.subject_id = s.id
        WHERE r.url IS NOT NULL AND r.url != ''
        ORDER BY r.id
    """
    rows = [dict(row) for row in conn.execute(sql)]
    conn.close()
    return rows[:limit] if limit else rows


def audit(limit: Optional[int] = None, workers: int = 12) -> dict:
    resources = load_resources(DB_PATH, limit)
    urls = sorted({r["url"] for r in resources})
    print(f"checking {len(urls)} distinct URLs across {len(resources)} resource rows...")

    started = time.time()
    results: dict[str, LinkCheck] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for index, check in enumerate(pool.map(fetch, urls), start=1):
            results[check.url] = check
            if index % 50 == 0:
                print(f"  {index}/{len(urls)} ({time.time() - started:.0f}s)")

    findings = []
    counts: Counter[str] = Counter()
    for resource in resources:
        check = results[resource["url"]]
        flags = classify(check, resource["provider"])
        for flag in flags:
            counts[flag] += 1
        if flags:
            findings.append(
                {
                    **{k: resource[k] for k in ("id", "topic_slug", "topic_name", "module_slug", "subject_name", "title", "provider", "role", "url", "verification_status")},
                    "flags": flags,
                    "status": check.status,
                    "final_url": check.final_url,
                    "content_type": check.content_type,
                    "page_title": check.page_title,
                    "error": check.error,
                }
            )

    report = {
        "checked_urls": len(urls),
        "checked_resources": len(resources),
        "elapsed_seconds": round(time.time() - started, 1),
        "flag_counts": dict(counts),
        "clean_resources": len(resources) - len({f["id"] for f in findings}),
        "findings": findings,
        "raw_checks": {url: asdict(check) for url, check in results.items()},
    }
    report["_checks"] = results  # kept out of the JSON dump; used by --record
    return report


def write_report(report: dict) -> tuple[Path, Path]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS / "resource_link_audit.json"
    serialisable = {k: v for k, v in report.items() if not k.startswith("_")}
    json_path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")

    lines = [
        "# Resource link audit",
        "",
        f"- URLs checked: **{report['checked_urls']}**",
        f"- Resource rows checked: **{report['checked_resources']}**",
        f"- Clean: **{report['clean_resources']}**",
        "",
        "| Flag | Rows |",
        "| --- | --- |",
    ]
    for flag, count in sorted(report["flag_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {flag} | {count} |")
    lines += ["", "## Findings", "", "| Module | Topic | Provider | Title | Flags | Status | URL |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for finding in report["findings"]:
        lines.append(
            "| {module_slug} | {topic_slug} | {provider} | {title} | {flags} | {status} | {url} |".format(
                module_slug=finding.get("module_slug") or "-",
                topic_slug=finding.get("topic_slug") or "-",
                provider=finding.get("provider") or "-",
                title=(finding.get("title") or "-").replace("|", "/")[:60],
                flags=",".join(finding["flags"]),
                status=finding.get("status") or finding.get("error") or "-",
                url=finding["url"],
            )
        )
    md_path = REPORTS / "resource_link_audit.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="check only the first N resource rows")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument(
        "--record",
        action="store_true",
        help="stamp last_verified_at and link evidence onto each resource row",
    )
    args = parser.parse_args()

    report = audit(args.limit, args.workers)
    json_path, md_path = write_report(report)
    print()
    print(f"clean: {report['clean_resources']}/{report['checked_resources']} resource rows")
    for flag, count in sorted(report["flag_counts"].items(), key=lambda kv: -kv[1]):
        print(f"  {flag}: {count}")
    print(f"\nwrote {json_path.name} and {md_path.name} to reports/")

    if args.record:
        stamped = record_evidence(DB_PATH, report["_checks"])
        print(f"stamped link evidence on {stamped} resource row(s)")


if __name__ == "__main__":
    main()
