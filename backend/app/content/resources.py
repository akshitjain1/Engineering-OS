"""First-class resource metadata for source-first delivery.

Does not invent URLs, video IDs, section names, or lecture titles.
Video IDs are extracted only from an existing watch/embed URL.
"""

from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

RESOURCE_ROLES = ("PRIMARY", "REFERENCE", "PRACTICE", "DEEP_DIVE")
VERIFIED = "VERIFIED"
TRUSTED = "TRUSTED"
NEEDS_REVIEW = "NEEDS_REVIEW"
BROKEN = "BROKEN"
UNRESOLVED = "UNRESOLVED"
ACTIVE_PRIMARY_STATUSES = {VERIFIED, TRUSTED}
KNOWN_VERIFICATION = {VERIFIED, TRUSTED, NEEDS_REVIEW, BROKEN, UNRESOLVED}

# YAML continues to use the legacy importer types. API/UI expose canonical types.
CANONICAL_TYPES = (
    "youtube",
    "documentation",
    "course",
    "lecture",
    "problem",
    "exercise",
    "specification",
    "repository",
    "other",
)

_LEGACY_TO_CANONICAL = {
    "youtube_video": "youtube",
    "youtube_playlist": "youtube",
    "documentation": "documentation",
    "article": "documentation",
    "book": "other",
    "interactive_tutorial": "course",
    "github_repo": "repository",
    "exercise": "exercise",
    "coding_problem": "problem",
    "other": "other",
    "youtube": "youtube",
    "course": "course",
    "lecture": "lecture",
    "problem": "problem",
    "specification": "specification",
    "repository": "repository",
}

_ROLE_TAG = re.compile(
    r"\s*\[(PRIMARY|REFERENCE|PRACTICE|DEEP_DIVE)\]\s*$",
    re.IGNORECASE,
)

_ACTIVITY_ROLE = {
    "LEARN": "PRIMARY",
    "REFERENCE": "REFERENCE",
    "PRACTICE": "PRACTICE",
}


def youtube_video_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    host = (parsed.hostname or "").replace("www.", "").lower()
    if host == "youtu.be":
        video = parsed.path.strip("/").split("/")[0]
        return video or None
    if "youtube.com" in host:
        query = parse_qs(parsed.query)
        if query.get("v"):
            return query["v"][0] or None
        parts = [part for part in (parsed.path or "").split("/") if part]
        if len(parts) >= 2 and parts[0] == "embed":
            return parts[1]
    return None


def is_youtube_playlist(url: Optional[str], resource_type: Optional[str] = None) -> bool:
    if (resource_type or "") == "youtube_playlist":
        return True
    if not url:
        return False
    if youtube_video_id(url):
        return False
    lowered = url.lower()
    return "playlist" in lowered or "list=" in lowered


def is_collection_url(url: Optional[str], resource_type: Optional[str] = None) -> bool:
    """True when the stored URL is a catalog/playlist/week hub, not one lecture/problem."""
    if is_youtube_playlist(url, resource_type):
        return True
    if not url:
        return False
    lowered = url.lower()
    if "/practice/practice/" in lowered:
        return True
    if "/weeks/" in lowered:
        return True
    if "/problemset" in lowered or "/studyplan" in lowered or "/problem-list" in lowered:
        return True
    return False


def canonical_resource_type(resource_type: Optional[str]) -> str:
    if not resource_type:
        return "other"
    if resource_type in CANONICAL_TYPES:
        return resource_type
    return _LEGACY_TO_CANONICAL.get(resource_type, "other")


def verification_for_url(url: Optional[str]) -> str:
    if not url or not str(url).strip():
        return UNRESOLVED
    try:
        parsed = urlparse(url)
    except ValueError:
        return UNRESOLVED
    if parsed.scheme != "https" or not parsed.netloc:
        return UNRESOLVED
    return VERIFIED


def extract_role_from_description(description: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if not description:
        return None, description
    match = _ROLE_TAG.search(description)
    if not match:
        return None, description
    role = match.group(1).upper()
    cleaned = _ROLE_TAG.sub("", description).rstrip()
    return role, cleaned or None


def metadata_from_spec(
    *,
    url: Optional[str],
    resource_type: str,
    role: Optional[str],
    section: Optional[str] = None,
    lecture: Optional[str] = None,
    video_id: Optional[str] = None,
    verification_status: Optional[str] = None,
) -> dict[str, Any]:
    extracted = youtube_video_id(url)
    stored_video = video_id or extracted
    if video_id and extracted and video_id != extracted:
        stored_video = extracted
    status = (verification_status or verification_for_url(url) or UNRESOLVED).upper()
    if status not in KNOWN_VERIFICATION:
        status = verification_for_url(url)
    # Map legacy UNRESOLVED for display as NEEDS_REVIEW in API; keep UNRESOLVED in DB for compat
    role_value = role.upper() if role else None
    if role_value not in RESOURCE_ROLES:
        role_value = None
    return {
        "role": role_value,
        "section": section,
        "lecture": lecture,
        "video_id": stored_video,
        "verification_status": status,
    }


def serialize_resource(resource: Any, *, for_learner: bool = True) -> dict[str, Any]:
    url = getattr(resource, "url", None) or None
    resource_type = getattr(resource, "resource_type", None)
    role = getattr(resource, "role", None)
    video_id = getattr(resource, "video_id", None) or youtube_video_id(url)
    raw_status = getattr(resource, "verification_status", None) or verification_for_url(url)
    # Learner-facing: content-verified statuses are mapped (never "SOURCE NOT MAPPED").
    status = NEEDS_REVIEW if raw_status == UNRESOLVED else raw_status
    playlist = is_youtube_playlist(url, resource_type)
    collection = is_collection_url(url, resource_type)
    from app.curriculum import is_lesson_complete, lesson_ui_status

    payload = {
        "id": resource.id,
        "slug": getattr(resource, "slug", None),
        "title": resource.title,
        "url": url,
        "resource_type": canonical_resource_type(resource_type),
        "source_resource_type": resource_type,
        "provider": getattr(resource, "provider", None),
        "role": role,
        "section": getattr(resource, "section", None),
        "lecture": getattr(resource, "lecture", None),
        "video_id": None if playlist else video_id,
        "verification_status": status,
        "resource_status": status,
        "is_playlist": playlist,
        "exact": bool(url) and raw_status in (VERIFIED, "VERIFIED_COVERAGE", "PARTIAL_COVERAGE") and not collection,
        "duration": resource.duration,
        "difficulty": resource.difficulty,
        "description": resource.description,
        "official_unofficial": resource.official_unofficial,
        "order_index": resource.order_index,
        "completion_status": lesson_ui_status(resource.completion_status),
        "completed": is_lesson_complete(resource.completion_status),
        "embeddable": bool(video_id) and not playlist and canonical_resource_type(resource_type) == "youtube",
        "learner_visible": bool(getattr(resource, "learner_visible", True) if getattr(resource, "learner_visible", None) is not None else True),
        "visibility_class": getattr(resource, "visibility_class", None) or "LEARNER",
    }
    payload["exactness"] = exactness_label(payload)
    payload["source_readiness"] = classify_primary(payload)
    payload["source_mapped"] = bool(url) and (raw_status or "").upper() not in ("", UNRESOLVED, "UNRESOLVED")
    return payload


def group_resources_by_role(
    resources: list[Any],
    *,
    for_learner: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    from app.content.learner_visibility import learner_facing_resources

    grouped = {role: [] for role in RESOURCE_ROLES}
    grouped["OTHER"] = []
    source = learner_facing_resources(resources) if for_learner else resources
    for resource in sorted(source, key=lambda item: (item.order_index or 0, item.id or 0)):
        payload = serialize_resource(resource, for_learner=for_learner)
        role = payload.get("role")
        # Treat PRIMARY_LEARN as PRIMARY for UI grouping
        if role == "PRIMARY_LEARN":
            role = "PRIMARY"
            payload["role"] = "PRIMARY"
        if role == "SUPPLEMENT":
            # Learner UI does not have a SUPPLEMENT section — skip for learner lists
            if for_learner:
                continue
            grouped["OTHER"].append(payload)
            continue
        if role in RESOURCE_ROLES:
            grouped[role].append(payload)
        else:
            grouped["OTHER"].append(payload)
    return grouped


def empty_source_fields() -> dict[str, Any]:
    return {
        "provider": None,
        "resource_title": None,
        "resource_type": None,
        "resource_url": None,
        "section": None,
        "lecture": None,
        "video_id": None,
        "verification_status": UNRESOLVED,
        "resource_status": UNRESOLVED,
        "is_playlist": False,
        "exact": False,
        "embeddable": False,
    }


def attach_source_fields(serialized: dict[str, Any]) -> dict[str, Any]:
    if not serialized.get("url"):
        return {**empty_source_fields(), "resource_title": serialized.get("title")}
    return {
        "provider": serialized.get("provider"),
        "resource_title": serialized.get("title"),
        "resource_type": serialized.get("resource_type"),
        "resource_url": serialized.get("url"),
        "section": serialized.get("section"),
        "lecture": serialized.get("lecture"),
        "video_id": serialized.get("video_id"),
        "verification_status": serialized.get("verification_status") or UNRESOLVED,
        "resource_status": serialized.get("verification_status") or UNRESOLVED,
        "is_playlist": serialized.get("is_playlist") or False,
        "exact": serialized.get("exact") or False,
        "embeddable": serialized.get("embeddable") or False,
    }


def select_resource_for_activity(resources: list[Any], activity_type: str) -> Optional[Any]:
    from app.content.learner_visibility import is_learner_visible

    wanted = _ACTIVITY_ROLE.get(activity_type)
    if not wanted:
        return None
    matches = [
        resource
        for resource in resources
        if getattr(resource, "role", None) == wanted
        and is_learner_visible(resource)
        and (getattr(resource, "verification_status", None) or "").upper() != BROKEN
    ]
    matches.sort(
        key=lambda item: (
            _status_rank(getattr(item, "verification_status", None)),
            0 if serialize_resource(item).get("embeddable") else 1,
            item.order_index or 0,
            item.id or 0,
        )
    )
    return matches[0] if matches else None


def _status_rank(status: Optional[str]) -> int:
    """Lower is better for primary selection. BROKEN is never preferred."""
    value = (status or UNRESOLVED).upper()
    if value == BROKEN:
        return 99
    if value in (VERIFIED, "VERIFIED_COVERAGE"):
        return 0
    if value == TRUSTED:
        return 1
    if value in (NEEDS_REVIEW, "PARTIAL_COVERAGE"):
        return 2
    return 3  # UNRESOLVED / unknown


def classify_primary(payload: Optional[dict[str, Any]]) -> str:
    if not payload or not payload.get("url"):
        return "UNRESOLVED"
    if payload.get("embeddable") and payload.get("exact"):
        return "READY_EXACT"
    if payload.get("is_playlist") or payload.get("exact") is False:
        return "READY_COLLECTION"
    return "READY_DOCUMENTATION"


def exactness_label(payload: dict[str, Any]) -> str:
    if not payload.get("url"):
        return "Unresolved"
    if payload.get("is_playlist"):
        return "Playlist"
    if payload.get("embeddable") and payload.get("exact"):
        return "Exact lecture"
    if payload.get("exact"):
        return "Exact page"
    return "Collection"


def orientation_from_description(description: Optional[str]) -> Optional[str]:
    """Return a short existing objective/blurb. Never generate new teaching copy."""
    if not description:
        return None
    objective = None
    for line in description.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("objective:"):
            objective = stripped.split(":", 1)[1].strip()
            break
    if objective and len(objective.split()) <= 40:
        return objective
    first = description.split("\n\n")[0].strip()
    if first.lower().startswith("objective:"):
        return None
    words = first.split()
    if 1 <= len(words) <= 40:
        return first
    return None


def lesson_ui_status(completion_status, progress=None):
    """Delegate to the canonical implementation in app.curriculum.

    Kept for backward compatibility with callers importing this name from
    here. Accepts both string and planner-lock-dict call signatures.
    """
    from app.curriculum import lesson_ui_status as _canonical

    return _canonical(completion_status, progress)
