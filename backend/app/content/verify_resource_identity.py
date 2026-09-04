"""Check that a resource's title and provider describe the page it points at.

Found on a DSA block: a card headed "NeetCode - Best Time to Buy and Sell
Stock", provider NeetCode, whose "Open official resource" button opened a
GeeksforGeeks article on asymptotic analysis. The URL was right for the topic.
The title and the provider were left over from something else entirely, so the
card described a page that does not exist.

A wrong link announces itself the moment you click it. A wrong title is worse:
you read it, believe you know what the source is, and find out only when the
page loads -- and on a day you are moving fast, maybe not even then.

The host decides. A URL is the one field that cannot be wrong about itself,
because it is what actually opens.

Facts come from the pages themselves and are cached to
`data/resource_identity.json`, so a rerun is offline and does not hammer anyone.

    python -m app.content.verify_resource_identity [--refresh] [--only 663,667]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic  # noqa: E402
from app.console import use_utf8  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

CACHE = Path(__file__).parent / "data" / "resource_identity.json"

EN_DASH = "–"
EM_DASH = "—"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

#: Hostnames that belong to the same organisation, so a provider naming one and
#: a URL using the other is not a mismatch.
SAME_ORG: list[set[str]] = [
    {"anthropic.com", "platform.claude.com"},
    {"dev.java", "docs.oracle.com", "oracle.com"},
    {"junit.org", "docs.junit.org"},
    {"ultralytics.com", "docs.ultralytics.com"},
    {"pytorch.org", "docs.pytorch.org", "raw.githubusercontent.com"},
    {"d2l.ai", "raw.githubusercontent.com"},
    {"huggingface.co", "raw.githubusercontent.com"},
    {"mlflow.org", "raw.githubusercontent.com"},
    {"scikit-learn.org", "raw.githubusercontent.com"},
    {"cs231n.github.io", "raw.githubusercontent.com"},
    {"developers.google.com", "raw.githubusercontent.com"},
]

#: Who owns a host. Only hosts whose owner is unambiguous are listed; anything
#: else is reported rather than renamed, because guessing a publisher's name is
#: exactly the kind of invention this module exists to remove.
HOST_PROVIDER: dict[str, str | None] = {
    "geeksforgeeks.org": "GeeksforGeeks",
    "nltk.org": "NLTK",
    "docs.langchain.com": "LangChain",
    "seeing-theory.brown.edu": "Seeing Theory",  # the name already on its sibling row
    "openstax.org": "OpenStax",
    "mathsisfun.com": "Math is Fun",
    "tutorial.math.lamar.edu": "Paul's Online Math Notes",
    "onlinestatbook.com": "Online StatBook",
    "promptingguide.ai": "Prompt Engineering Guide",
    "khanacademy.org": "Khan Academy",
    "neetcode.io": "NeetCode",
    "leetcode.com": "LeetCode",
    "developer.mozilla.org": "MDN",
    # The provider of a YouTube video is its channel, which the host cannot
    # tell us, so these are never rewritten.
    "youtube.com": None,
}

#: How a provider is written when it opens a title. Only GeeksforGeeks differs
#: from its own name, and only because 30-odd existing rows already read "GFG".
TITLE_PREFIX = {"GeeksforGeeks": "GFG"}

#: Attributions a title may open with. A title starting with one of these is
#: claiming a publisher, so when the publisher turns out to be wrong, the title
#: is wrong with it and gets rebuilt from the page.
ATTRIBUTIONS = (
    "GFG", "GeeksforGeeks", "NeetCode", "MDN", "IBM", "Khan Academy",
    "Hugging Face LLM Course", "Hugging Face", "OpenAI", "Seeing Theory",
    "LeetCode", "NLTK", "LangChain", "OpenStax",
)

#: Separators a page puts between its own title and its site name.
SEPARATORS = (" | ", " - ", f" {EN_DASH} ", f" {EM_DASH} ")

#: Site names pages append to (or prepend to) their own titles. Stripped so a
#: card does not end up reading "GFG - Heap Sort - GeeksforGeeks".
SITE_NAMES = (
    "GeeksforGeeks", "OpenStax", "Prompt Engineering Guide", "Docs by LangChain",
    "Seeing Theory", "Khan Academy", "MDN Web Docs", "NeetCode", "LeetCode",
)


def host_of(url: str | None) -> str:
    return (urlparse(url or "").hostname or "").replace("www.", "")


def same_org(a: str, b: str) -> bool:
    return a == b or any({a, b} <= group for group in SAME_ORG)


def page_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip() or None


def clean_page_title(raw: str | None) -> str:
    """The page's own title, without the site name it repeats around it.

    Plain string operations rather than one regex. An earlier version wrote the
    en and em dashes as escapes inside a raw string, so the pattern hunted for
    the literal text "backslash-u-2-0-1-3", stripped nothing, and looked
    entirely correct while doing so.
    """
    title = re.sub(r"<!--.*?-->", "", raw or "").strip()
    for site in SITE_NAMES:
        for sep in SEPARATORS:
            suffix, prefix = f"{sep}{site}", f"{site}{sep}"
            if title.endswith(suffix):
                title = title[: -len(suffix)]
            if title.startswith(prefix):
                title = title[len(prefix) :]
    return re.sub(r"\s+", " ", title).strip(f" -|{EN_DASH}{EM_DASH}")


def opens_with_attribution(title: str | None) -> str | None:
    """The publisher a title claims, if it opens by claiming one."""
    for name in sorted(ATTRIBUTIONS, key=len, reverse=True):
        pattern = "^" + re.escape(name) + r"\s*[:" + EN_DASH + EM_DASH + r"-]\s+"
        if re.match(pattern, title or ""):
            return name
    return None


def load_cache() -> dict[str, Any]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def fetch_titles(urls: list[str], refresh: bool = False) -> dict[str, Any]:
    facts = {} if refresh else load_cache()
    missing = [u for u in urls if u not in facts]
    if missing:
        with httpx.Client(follow_redirects=True, timeout=25) as client:
            for i, url in enumerate(missing, 1):
                entry: dict[str, Any] = {"url": url}
                try:
                    resp = client.get(url, headers=_HEADERS)
                    entry["status"] = resp.status_code
                    entry["final_host"] = host_of(str(resp.url))
                    if resp.status_code == 200:
                        entry["page_title"] = page_title(resp.text)
                except Exception as exc:  # noqa: BLE001
                    entry["error"] = f"{type(exc).__name__}: {exc}"
                facts[url] = entry
                if i % 5 == 0:
                    print(f"  ... {i}/{len(missing)}")
                time.sleep(0.4)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(facts, indent=2, sort_keys=True), encoding="utf-8")
    return facts


def rows(db) -> list[Any]:
    return (
        db.query(CurriculumResource, CurriculumTopic.name)
        .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
        .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
        .filter(CurriculumResource.url.isnot(None), CurriculumResource.url != "")
        .all()
    )


def provider_mismatches(db) -> list[dict[str, Any]]:
    """Discovery: rows whose provider sits on a host it is rarely used with.

    A provider's real host is the one it is used with most often, which makes
    this self-correcting -- NeetCode sits on neetcode.io 128 times and on
    geeksforgeeks.org 6 times, so the six are the anomaly. Providers used on a
    single host are never flagged. This is deliberately broader than
    `corrections`: it surfaces hosts nobody has judged yet.
    """
    all_rows = rows(db)
    hosts: dict[str, Counter] = defaultdict(Counter)
    for resource, _ in all_rows:
        if resource.provider and resource.learner_visible is not False:
            hosts[resource.provider][host_of(resource.url)] += 1

    out = []
    for resource, topic_name in all_rows:
        if not resource.provider or resource.learner_visible is False:
            continue
        counts = hosts[resource.provider]
        if len(counts) < 2:
            continue
        host = host_of(resource.url)
        top = counts.most_common()
        if any(same_org(host, h) for h, n in top if n == top[0][1]):
            continue
        out.append({
            "id": resource.id,
            "title": resource.title,
            "provider": resource.provider,
            "url": resource.url,
            "host": host,
            "topic": topic_name,
            "usual_host": top[0][0],
        })
    return out


def corrections(db, facts: dict[str, Any]) -> list[dict[str, Any]]:
    """Every row whose provider contradicts a host with an unambiguous owner.

    The title is only rewritten when it opens by naming a publisher, because
    that is the part that turns out to be false. A title that merely describes
    the content ("Bayes theorem") is left alone even when the page's own title
    is something useless like "406".
    """
    out = []
    for resource, topic_name in rows(db):
        if resource.learner_visible is False:
            continue
        owner = HOST_PROVIDER.get(host_of(resource.url))
        if not owner or (resource.provider or "") == owner:
            continue

        change: dict[str, Any] = {
            "id": resource.id,
            "topic": topic_name,
            "url": resource.url,
            "provider_from": resource.provider,
            "provider_to": owner,
            "title_from": resource.title,
            "title_to": None,
        }
        claimed = opens_with_attribution(resource.title)
        if claimed and claimed != TITLE_PREFIX.get(owner, owner):
            cleaned = clean_page_title((facts.get(resource.url) or {}).get("page_title"))
            if cleaned:
                change["title_to"] = f"{TITLE_PREFIX.get(owner, owner)} {EM_DASH} {cleaned}"
        out.append(change)
    return out


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="ignore the cache")
    parser.add_argument("--only", help="comma-separated resource ids")
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        flagged = provider_mismatches(db)
        if args.only:
            wanted = {int(x) for x in args.only.split(",")}
            flagged = [f for f in flagged if f["id"] in wanted]
        facts = fetch_titles([f["url"] for f in flagged], refresh=args.refresh)
        proposed = corrections(db, facts)
    finally:
        db.close()

    print(f"{len(flagged)} resource(s) flagged by host frequency")
    print(f"{len(proposed)} of them sit on a host whose owner is unambiguous\n")
    for change in sorted(proposed, key=lambda c: c["id"]):
        print(f"  id {change['id']:<5} {change['provider_from']} -> {change['provider_to']}")
        if change["title_to"]:
            print(f"        {change['title_from']}")
            print(f"     -> {change['title_to']}")
    print(f"\n  facts cached at {CACHE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
