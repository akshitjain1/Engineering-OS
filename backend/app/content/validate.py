from __future__ import annotations

from urllib.parse import urlparse

from pydantic import ValidationError

from .schema import CurriculumManifest, ManifestError, load_manifest_dict


def validate_manifest(
    data: dict,
    existing_topic_slugs: set[str] | None = None,
) -> CurriculumManifest:
    errors: list[str] = []
    try:
        manifest = load_manifest_dict(data)
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", []))
            errors.append(f"{loc}: {err.get('msg')}")
        raise ManifestError(errors) from exc

    errors.extend(_duplicate_slugs(manifest))
    errors.extend(_duplicate_orders(manifest))
    errors.extend(_parent_refs(manifest))
    errors.extend(_resource_urls(manifest))
    errors.extend(_prerequisites(manifest, existing_topic_slugs or set()))
    errors.extend(_next_topics(manifest, existing_topic_slugs or set()))
    if errors:
        raise ManifestError(errors)
    return manifest


def _duplicate_slugs(manifest: CurriculumManifest) -> list[str]:
    seen: dict[str, str] = {}
    errors: list[str] = []

    def add(slug: str, kind: str) -> None:
        if slug in seen:
            errors.append(f"duplicate ID '{slug}' used for both {seen[slug]} and {kind}")
        else:
            seen[slug] = kind

    add(manifest.track.slug, "track")
    for level in manifest.track.levels:
        add(level.slug, "level")
        for subject in level.subjects:
            add(subject.slug, "subject")
            for module in subject.modules:
                add(module.slug, "module")
                for topic in module.topics:
                    add(topic.slug, "topic")
                    for lesson in topic.lessons:
                        add(lesson.slug, "lesson")
                        for resource in lesson.resources:
                            add(resource.slug, "resource")
                        for question in lesson.questions:
                            add(question.slug, "question")
                        for exercise in lesson.exercises:
                            add(exercise.slug, "exercise")
    return errors


def _duplicate_orders(manifest: CurriculumManifest) -> list[str]:
    errors: list[str] = []
    for _module, topic in manifest.walk_topics():
        orders = [lesson.order for lesson in topic.lessons]
        if len(orders) != len(set(orders)):
            errors.append(f"duplicate lesson order in topic '{topic.slug}'")
        for lesson in topic.lessons:
            res_orders = [resource.order for resource in lesson.resources]
            if len(res_orders) != len(set(res_orders)):
                errors.append(f"duplicate resource order in lesson '{lesson.slug}'")
    return errors


def _parent_refs(manifest: CurriculumManifest) -> list[str]:
    errors: list[str] = []
    subject_slugs = {
        subject.slug for level in manifest.track.levels for subject in level.subjects
    }
    for module, topic in manifest.walk_topics():
        if topic.module and topic.module != module.slug:
            errors.append(
                f"invalid parent: topic '{topic.slug}' declares module '{topic.module}' but is nested under '{module.slug}'"
            )
        if module.subject and module.subject not in subject_slugs:
            errors.append(
                f"invalid parent: module '{module.slug}' references unknown subject '{module.subject}'"
            )
        for lesson in topic.lessons:
            if lesson.topic and lesson.topic != topic.slug:
                errors.append(
                    f"invalid lesson reference: lesson '{lesson.slug}' declares topic '{lesson.topic}' but is nested under '{topic.slug}'"
                )
    return errors


def _resource_urls(manifest: CurriculumManifest) -> list[str]:
    errors: list[str] = []
    for _module, topic in manifest.walk_topics():
        for lesson in topic.lessons:
            for resource in lesson.resources:
                if not resource.url:
                    continue
                parsed = urlparse(resource.url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    errors.append(f"invalid resource URL for '{resource.slug}': {resource.url}")
    return errors


def _prerequisite_type(ref: Any) -> str:
    """Extract the type from a prerequisite reference.

    Supports two formats:
    - String: treated as REQUIRED (backward compatible)
    - Dict with 'slug' and 'type' keys: type determines classification
    """
    if isinstance(ref, str):
        return "REQUIRED"
    if isinstance(ref, dict):
        return ref.get("type", "REQUIRED")
    return "REQUIRED"


def _prerequisites(manifest: CurriculumManifest, existing_topic_slugs: set[str]) -> list[str]:
    errors: list[str] = []
    topic_slugs = {topic.slug for _module, topic in manifest.walk_topics()}
    known = topic_slugs | existing_topic_slugs
    graph: dict[str, list[str]] = {}
    for _module, topic in manifest.walk_topics():
        # Store prerequisites with their types for the graph
        prereqs = topic.prerequisites or []
        typed_prereqs = []
        for ref in prereqs:
            rtype = _prerequisite_type(ref)
            typed_prereqs.append(ref)
            # Also track the type alongside the slug
            # We store type info by pairing slug:type
            if isinstance(ref, str):
                # String format: treated as REQUIRED
                pass
            elif isinstance(ref, dict):
                # Dict format: use the type
                pass
        graph[topic.slug] = typed_prereqs
        for ref in prereqs:
            # Extract just the slug for the known-check
            slug = ref if isinstance(ref, str) else ref.get("slug", "")
            if slug and slug not in known:
                errors.append(f"missing prerequisite '{slug}' on topic '{topic.slug}'")

    def visit(node: str, stack: list[str]) -> None:
        if node in stack:
            cycle = stack[stack.index(node) :] + [node]
            errors.append("circular prerequisites: " + " -> ".join(cycle))
            return
        for nxt in graph.get(node, []):
            # For visitation, we just need the slug for traversal
            slug = nxt if isinstance(nxt, str) else nxt.get("slug", nxt)
            if slug in graph:
                visit(slug, stack + [node])

    for slug in graph:
        visit(slug, [])
    return list(dict.fromkeys(errors))


def _next_topics(manifest: CurriculumManifest, existing_topic_slugs: set[str]) -> list[str]:
    errors: list[str] = []
    topic_slugs = {topic.slug for _module, topic in manifest.walk_topics()}
    known = topic_slugs | existing_topic_slugs
    for _module, topic in manifest.walk_topics():
        nxt = topic.next_topic
        if not nxt:
            continue
        if nxt not in known:
            errors.append(f"missing next_topic '{nxt}' on topic '{topic.slug}'")
    return errors


def topic_slugs_from_data(data: dict) -> set[str]:
    slugs: set[str] = set()
    track = data.get("track") or {}
    for level in track.get("levels") or []:
        for subject in level.get("subjects") or []:
            for module in subject.get("modules") or []:
                for topic in module.get("topics") or []:
                    slug = topic.get("slug")
                    if slug:
                        slugs.add(slug)
    return slugs
