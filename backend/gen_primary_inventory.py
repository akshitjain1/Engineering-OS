import json
from collections import Counter
from pathlib import Path

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
from app.db.session import SessionLocal


REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def normalize_url(url):
    if not url:
        return ""
    return url.rstrip("/")


def main():
    db = SessionLocal()

    try:
        topics = (
            db.query(CurriculumTopic)
            .order_by(CurriculumTopic.domain_key, CurriculumTopic.order_index)
            .all()
        )

        all_resources = (
            db.query(CurriculumResource)
            .join(CurriculumLesson, CurriculumResource.lesson_id == CurriculumLesson.id)
            .filter(CurriculumResource.learner_visible.is_(True))
            .all()
        )

        resources_by_topic = {}

        for resource in all_resources:
            if resource.role == "PRIMARY" and resource.lesson:
                topic_id = resource.lesson.topic_id
                resources_by_topic.setdefault(topic_id, []).append(resource)
        inventory = []
        zero_primary = []
        multiple_primary = []

        for topic in topics:
            primaries = resources_by_topic.get(topic.id, [])

            if topic.topic_type == "NON_LEARNABLE_CONTAINER":
                continue

            if len(primaries) == 0:
                zero_primary.append(
                    {
                        "topic_slug": topic.slug,
                        "topic_name": topic.name,
                        "domain": topic.domain_key,
                    }
                )

            if len(primaries) > 1:
                multiple_primary.append(
                    {
                        "topic_slug": topic.slug,
                        "topic_name": topic.name,
                        "domain": topic.domain_key,
                        "primary_count": len(primaries),
                    }
                )

            for resource in primaries:
                inventory.append(
                    {
                        "topic_slug": topic.slug,
                        "topic_name": topic.name,
                        "domain": topic.domain_key,
                        "topic_order": topic.order_index,

                        "resource_slug": resource.slug,
                        "title": resource.title,
                        "provider": resource.provider,
                        "url": resource.url,
                        "normalized_url": normalize_url(resource.url),

                        "resource_type": resource.resource_type,
                        "role": resource.role,
                        "learner_visible": resource.learner_visible,

                        "boundary_type": resource.boundary_type,
                        "start_timestamp": resource.start_timestamp,
                        "end_timestamp": resource.end_timestamp,
                        "section_start": resource.start_boundary,
                        "section_end": resource.end_boundary,

                        "exactness": resource.exactness,
                        "verification_status": resource.verification_status,
                        "video_id": resource.video_id,
                        "learner_instruction": resource.description,
                    }
                )

        url_counter = Counter(
            item["normalized_url"]
            for item in inventory
            if item["normalized_url"]
        )

        reused_urls = [
            {
                "url": url,
                "count": count,
                "topics": [
                    item["topic_slug"]
                    for item in inventory
                    if item["normalized_url"] == url
                ],
            }
            for url, count in url_counter.most_common()
            if count > 1
        ]

        boundary_missing = [
            item
            for item in inventory
            if item["boundary_type"] in {
                "ARTICLE_SECTION",
                "VIDEO_TIMESTAMP",
                "SECTION",
            }
            and not (
                item["start_timestamp"]
                or item["section_start"]
            )
        ]

        homepage_like = []

        for item in inventory:
            url = item["normalized_url"]

            if not url:
                continue

            path = url.replace("https://", "").replace("http://", "")
            path = path.split("/", 1)

            if len(path) == 1 or not path[1].strip():
                homepage_like.append(item)

        missing_instruction = [
            item
            for item in inventory
            if not item["learner_instruction"]
            or not item["learner_instruction"].strip()
        ]

        missing_provider = [
            item
            for item in inventory
            if not item["provider"]
            or not item["provider"].strip()
        ]

        missing_title = [
            item
            for item in inventory
            if not item["title"]
            or not item["title"].strip()
        ]

        by_domain = Counter(
            item["domain"]
            for item in inventory
        )

        output = {
            "summary": {
                "learner_visible_topics": len(
                    [
                        t
                        for t in topics
                        if t.topic_type != "NON_LEARNABLE_CONTAINER"
                    ]
                ),
                "learner_visible_primary_resources": len(inventory),
                "topics_with_zero_primary": len(zero_primary),
                "topics_with_multiple_primary": len(multiple_primary),
                "boundary_missing": len(boundary_missing),
                "homepage_like": len(homepage_like),
                "missing_instruction": len(missing_instruction),
                "missing_provider": len(missing_provider),
                "missing_title": len(missing_title),
                "distinct_primary_urls": len(url_counter),
            },
            "topics_with_zero_primary": zero_primary,
            "topics_with_multiple_primary": multiple_primary,
            "reused_urls": reused_urls,
            "boundary_missing": boundary_missing,
            "homepage_like": homepage_like,
            "missing_instruction": missing_instruction,
            "missing_provider": missing_provider,
            "missing_title": missing_title,
            "count_by_domain": dict(sorted(by_domain.items())),
            "inventory": inventory,
        }

        REPORTS_DIR.mkdir(exist_ok=True)

        json_path = REPORTS_DIR / "current_primary_resource_inventory.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                output,
                f,
                indent=2,
                ensure_ascii=False,
            )

        md_path = REPORTS_DIR / "current_primary_resource_inventory.md"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Current Primary Resource Inventory\n\n")

            f.write("## Summary\n\n")

            for key, value in output["summary"].items():
                f.write(f"- **{key}:** {value}\n")

            f.write("\n## Count by Domain\n\n")

            for domain, count in sorted(by_domain.items()):
                f.write(f"- **{domain}:** {count}\n")

            f.write("\n## Topics With Zero PRIMARY\n\n")

            if zero_primary:
                for item in zero_primary:
                    f.write(
                        f"- `{item['topic_slug']}` — "
                        f"{item['topic_name']} "
                        f"({item['domain']})\n"
                    )
            else:
                f.write("None\n")

            f.write("\n## Topics With Multiple PRIMARY Resources\n\n")

            if multiple_primary:
                for item in multiple_primary:
                    f.write(
                        f"- `{item['topic_slug']}` — "
                        f"{item['primary_count']} PRIMARY resources\n"
                    )
            else:
                f.write("None\n")

            f.write("\n## Reused URLs\n\n")

            for item in reused_urls:
                f.write(
                    f"### {item['count']}× `{item['url']}`\n\n"
                )

                for slug in item["topics"]:
                    f.write(f"- `{slug}`\n")

                f.write("\n")

            f.write("\n## Boundary Missing\n\n")

            for item in boundary_missing:
                f.write(
                    f"- `{item['topic_slug']}` — "
                    f"`{item['resource_slug']}` — "
                    f"{item['url']}\n"
                )

            f.write("\n## Homepage-like URLs\n\n")

            for item in homepage_like:
                f.write(
                    f"- `{item['topic_slug']}` — "
                    f"`{item['url']}`\n"
                )

            f.write("\n# Complete Inventory\n\n")

            f.write(
                "| Domain | Topic | Resource | Provider | URL | "
                "Boundary | Exactness |\n"
            )

            f.write(
                "|---|---|---|---|---|---|---|\n"
            )

            for item in inventory:
                f.write(
                    f"| {item['domain']} "
                    f"| {item['topic_slug']} "
                    f"| {item['resource_slug']} "
                    f"| {item['provider']} "
                    f"| {item['url']} "
                    f"| {item['boundary_type']} "
                    f"| {item['exactness']} |\n"
                )

        print(json.dumps(
            output["summary"],
            indent=2,
        ))

        print()
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")

    finally:
        db.close()


if __name__ == "__main__":
    main()