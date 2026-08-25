import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

from inspect_new_primaries import fetch, parse

BASE = "https://raw.githubusercontent.com/huggingface/course/main/chapters/en"
for rel in ["chapter2/7.mdx", "chapter2/2.mdx", "chapter3/3.mdx", "chapter1/1.mdx",
            "chapter7/5.mdx", "chapter7/6.mdx", "chapter11/8.mdx"]:
    cls, code, payload = fetch(f"{BASE}/{rel}")
    if cls != "OK":
        print(rel, "->", cls, code)
        continue
    h, v = parse(payload)
    title = next((t for l, t in h if t.strip()), "?")
    low = v.lower()
    flags = {k: (k in low) for k in ["masked", "bidirectional", "decoder", "perplexity", "bleu", "bpe", "attention"]}
    print(rel, "|", title[:60], "| heads:", len(h), "|", {k: v2 for k, v2 in flags.items() if v2})
