"""Apply verified Domain 0 content onto the official YAML without touching prereqs/next_topic."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _d0_part6 import CONTENT  # noqa: E402

YAML_PATH = HERE / "curriculum" / "foundation" / "00-computer-developer-foundations.yaml"


def iter_topics(data: dict):
    for level in data["track"]["levels"]:
        for subject in level["subjects"]:
            for module in subject["modules"]:
                for topic in module["topics"]:
                    yield topic


def apply() -> None:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    found = []
    for topic in iter_topics(data):
        slug = topic["slug"]
        found.append(slug)
        if slug not in CONTENT:
            raise SystemExit(f"missing content for {slug}")
        unit = CONTENT[slug]
        prereqs = list(topic.get("prerequisites") or [])
        nxt = topic.get("next_topic")
        topic["description"] = unit["explanation"]
        if unit.get("learning_objective"):
            topic["learning_objective"] = unit["learning_objective"]
        topic["mastery_criteria"] = list(unit["mastery_criteria"])
        topic["prerequisites"] = prereqs
        topic["next_topic"] = nxt
        lesson = topic["lessons"][0]
        lesson["description"] = unit["explanation"]
        lesson["hours_estimated"] = float(unit["hours_estimated"])
        lesson["resources"] = unit["resources"]
        lesson["questions"] = unit["questions"]
        lesson["exercises"] = unit["exercises"]

    missing = set(CONTENT) - set(found)
    extra = set(found) - set(CONTENT)
    if missing or extra:
        raise SystemExit(f"slug mismatch missing={sorted(missing)} extra={sorted(extra)}")
    YAML_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    n_q = n_ex = n_p = n_r = n_pr = n_d = n_unmapped = 0
    unmapped = []
    for slug, unit in CONTENT.items():
        n_q += len(unit["questions"])
        n_ex += len(unit["exercises"])
        roles = {res["role"]: res for res in unit["resources"]}
        for res in unit["resources"]:
            if res["role"] == "PRIMARY":
                n_p += 1
            elif res["role"] == "REFERENCE":
                n_r += 1
            elif res["role"] == "PRACTICE":
                n_pr += 1
            elif res["role"] == "DEEP_DIVE":
                n_d += 1
        has_primary_url = any(res["role"] == "PRIMARY" and res.get("url") for res in unit["resources"])
        if not has_primary_url:
            n_unmapped += 1
            unmapped.append(slug)
    print(
        f"topics={len(CONTENT)} questions={n_q} exercises={n_ex} "
        f"PRIMARY={n_p} REFERENCE={n_r} PRACTICE={n_pr} DEEP_DIVE={n_d} "
        f"no_primary_url={n_unmapped}"
    )
    print("no_primary_url:", ", ".join(unmapped))


if __name__ == "__main__":
    apply()
