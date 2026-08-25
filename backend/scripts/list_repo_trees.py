"""Resolve real file paths in d2l-en / hf-course repos via GitHub trees API."""
import json
import urllib.request

UA = {"User-Agent": "engineering-os-inspector", "Accept": "application/vnd.github+json"}


def tree(repo, ref="master"):
    url = f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=0"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def list_dir(repo, ref, path):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return [it["name"] for it in json.load(r)]


out = {}
for path in [
    "chapter_introduction", "chapter_linear-regression", "chapter_multilayer-perceptrons",
    "chapter_optimization", "chapter_convolutional-neural-networks", "chapter_convolutional-modern",
    "chapter_recurrent-neural-networks", "chapter_recurrent-modern", "chapter_attention-mechanisms",
    "chapter_object-detection", "chapter_computer-vision",
    "chapter_natural-language-processing-pretraining",
]:
    try:
        names = [n for n in list_dir("d2l-ai/d2l-en", "master", path) if n.endswith(".md")]
        out[path] = names
        print(path, "->", len(names), "files")
    except Exception as e:
        print(path, "ERR", e)

try:
    ch = [n for n in list_dir("huggingface/course", "main", "chapters/en") ]
    print("hf chapters/en:", ch)
    out["hf_chapters_en"] = ch
except Exception as e:
    print("hf err", e)

json.dump(out, open(r"reports\repo_trees.json", "w", encoding="utf-8"), indent=2)
