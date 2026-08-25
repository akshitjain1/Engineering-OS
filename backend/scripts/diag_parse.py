import json
import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

from inspect_new_primaries import fetch, parse

cls, code, payload = fetch("https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_object-detection/ssd.md")
print("ssd.md ->", cls, code)
h, v = parse(payload)
print("headings:", len(h), [x[1][:50] for x in h[:6]])
print("chars:", len(v))
print("has 'non-maximum suppression':", "non-maximum suppression" in v.lower())
print("has 'iou':", "iou" in v.lower())

d = json.load(open(r"reports/resource_evidence_final.json", encoding="utf-8"))
print("\n=== current GAPS ===")
for r in d["resources"]:
    if r["classification"] == "RESOURCE_GAP":
        print(f"  {r['topic_slug']} | {r['unmatched']} | {r['url'][:90]}")
