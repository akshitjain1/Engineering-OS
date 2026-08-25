import json

d = json.load(open(r"reports/resource_evidence_final.json", encoding="utf-8"))
rs = d["resources"]

print("=== NEEDS_REVIEW ===")
for r in rs:
    if r["classification"] == "NEEDS_REVIEW":
        print(" ", r["resource_slug"], "|", r["url"])

print("\n=== RESOURCE_GAP (slug | missing concepts | url) ===")
for r in rs:
    if r["classification"] == "RESOURCE_GAP":
        print(f"  {r['topic_slug']} | {r['unmatched']} | {r['url'][:95]}")

print("\n=== PARTIAL unmatched sample ===")
n = 0
for r in rs:
    if r["classification"] == "PARTIAL_COVERAGE":
        print(f"  {r['topic_slug']} | missing {r['unmatched']}")
        n += 1
        if n >= 12:
            break
