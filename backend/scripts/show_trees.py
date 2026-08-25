import json

t = json.load(open(r"reports\repo_trees.json", encoding="utf-8"))
for k in ("chapter_object-detection", "chapter_attention-mechanisms"):
    pass
# Those two 404'd — find their real names from the earlier full listing attempt:
print(json.dumps(t, indent=2)[:4000])
