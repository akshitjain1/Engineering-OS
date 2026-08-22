"""Final URL replacements for the last unresolved topics + re-verify."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from app.content.audit import audit_all
from app.content.demote_weak_verification import demote_weak_verification
from app.content.lockdown_normalize import apply_lockdown_normalization
from app.content.lockdown_verify_v2 import verify_domains
from app.content.verification import VERIFICATION_NEEDS_REVIEW
from app.db.models import CurriculumResource
from app.db.session import SessionLocal

FINAL_URLS: dict[str, dict] = {
    "math-vectors-primary": {
        "url": "https://mathinsight.org/vector_introduction",
        "section": "Introduction to vectors",
    },
    "math-matrices-primary": {
        "url": "https://mathinsight.org/matrix_introduction",
        "section": "Introduction to matrices",
    },
    "math-probability-primary": {
        "url": "https://seeing-theory.brown.edu/basic-probability/index.html",
        "section": "Basic probability",
    },
    "math-stats-summary-primary": {
        "url": "https://openstax.org/books/introductory-statistics/pages/2-5-measures-of-the-center-of-the-data",
        "section": "Measures of the center of the data",
    },
    "math-gradient-intuition-primary": {
        "url": "https://openstax.org/books/calculus-volume-3/pages/4-6-directional-derivatives-and-the-gradient",
        "section": "Directional derivatives and the gradient",
    },
    "se-solid-srp-primary": {
        "url": "https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html",
        "section": "Single Responsibility Principle",
    },
    "se-solid-ocp-primary": {
        "url": "https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html",
        "section": "Open Closed Principle",
    },
    "se-requirements-primary": {
        "url": "https://www.geeksforgeeks.org/software-engineering-requirements-engineering-process/",
        "section": "Requirements engineering process",
    },
    "net-dns-primary": {
        "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_domain_name",
        "section": "What is a domain name / DNS",
    },
    "net-tcp-udp-primary": {
        "url": "https://www.rfc-editor.org/rfc/rfc793",
        "section": "TCP specification overview (contrast with UDP datagrams)",
    },
    "dsa-hash-map-learn-exact": {
        "url": "https://docs.oracle.com/javase/tutorial/collections/implementations/map.html",
        "section": "Map implementations / HashMap",
    },
    "dsa-lookup-patterns-learn-exact": {
        "url": "https://www.geeksforgeeks.org/check-if-pair-with-given-sum-exists-in-array/",
        "section": "Pair with given sum / complement lookup",
    },
    "dsa-permutations-learn-exact": {
        "url": "https://www.geeksforgeeks.org/write-a-c-program-to-print-all-permutations-of-a-given-string/",
        "section": "Print all permutations",
    },
    "dsa-dp-state-learn-exact": {
        "url": "https://www.geeksforgeeks.org/overlapping-subproblems-property-in-dynamic-programming-dp-1/",
        "section": "Overlapping subproblems / DP state thinking",
    },
    "dsa-dp-transition-learn-exact": {
        "url": "https://www.geeksforgeeks.org/tabulation-vs-memoization/",
        "section": "Tabulation vs memoization transitions",
    },
    "dsa-interview-hygiene-learn-exact": {
        "url": "https://www.techinterviewhandbook.org/coding-interview-techniques/",
        "section": "Coding interview techniques",
    },
    "ml-features-labels-primary": {
        "url": "https://scikit-learn.org/stable/getting_started.html",
        "section": "Getting started — features and estimators",
    },
    "ai-eng-awareness-primary": {
        "url": "https://platform.openai.com/docs/guides/evals",
        "section": "Evals for reliable LLM features",
    },
}


def main() -> None:
    db = SessionLocal()
    now = datetime.now(timezone.utc).isoformat()
    fixed = 0
    for slug, spec in FINAL_URLS.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
        if not row:
            print("missing", slug)
            continue
        row.url = spec["url"]
        row.section = spec["section"][:200]
        row.verification_status = VERIFICATION_NEEDS_REVIEW
        row.required_concepts_covered = []
        row.last_verified_at = now
        fixed += 1
    db.commit()
    print("fixed", fixed)

    domains = [
        "dsa",
        "mathematics",
        "software-engineering",
        "networking",
        "ml",
        "ai-engineering",
    ]
    for d in domains:
        print("===", d, verify_domains(db, domains=[d], workers=10))
        db.commit()

    print("norm", apply_lockdown_normalization(db))
    print("demote", demote_weak_verification(db))
    db.commit()
    sc = dict(Counter(a.readiness for a in audit_all(db)))
    print("SCORECARD", sc)
    non = [a for a in audit_all(db) if a.readiness != "READY"]
    print("nonready", len(non))
    for a in sorted(non, key=lambda x: (x.domain_key or "", x.topic_slug)):
        print(f"  {a.readiness:18} {a.domain_key:18} {a.topic_slug}")
    db.close()


if __name__ == "__main__":
    main()
