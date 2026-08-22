from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
RESOURCE_TYPES = {
    "youtube_video",
    "youtube_playlist",
    "documentation",
    "article",
    "book",
    "interactive_tutorial",
    "github_repo",
    "exercise",
    "coding_problem",
    "other",
    "youtube",
    "course",
    "lecture",
    "problem",
    "specification",
    "repository",
}


class ManifestError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Curriculum manifest is invalid:\n- " + "\n- ".join(errors))


RESOURCE_ROLES = {"PRIMARY", "REFERENCE", "PRACTICE", "DEEP_DIVE"}
VERIFICATION_STATUSES = {
    "VERIFIED",
    "TRUSTED",
    "NEEDS_REVIEW",
    "BROKEN",
    "UNRESOLVED",
}
LEARNING_TRACKS = {"CORE", "SPECIALIZATION", "ALWAYS_ON", "BUILD", "OPTIONAL"}
DEPTH_TARGETS = {"AWARENESS", "WORKING_KNOWLEDGE", "STRONG", "DEEP"}


class ResourceSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str
    type: str = "other"
    url: Optional[str] = None
    provider: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    difficulty: Optional[str] = None
    official: bool = True
    order: int = 0
    section: Optional[str] = None
    lecture: Optional[str] = None
    video_id: Optional[str] = None
    verification_status: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_ok(cls, value: str) -> str:
        if value not in RESOURCE_TYPES:
            raise ValueError(f"unsupported resource type '{value}'")
        return value

    @field_validator("role")
    @classmethod
    def role_ok(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in RESOURCE_ROLES:
            raise ValueError(f"unsupported resource role '{value}'")
        return value

    @field_validator("verification_status")
    @classmethod
    def verification_ok(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        upper = value.upper()
        if upper not in VERIFICATION_STATUSES:
            raise ValueError(f"unsupported verification_status '{value}'")
        return upper


class QuestionSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    prompt: str
    options: list[str] = Field(min_length=2)
    answer: str
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    mastery_requirement: bool = False

    @model_validator(mode="after")
    def answer_in_options(self) -> "QuestionSpec":
        if self.answer not in self.options:
            raise ValueError(f"answer for '{self.slug}' must be one of the options")
        return self


class ExerciseSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str
    instructions: str
    difficulty: str = "beginner"
    order: int = 0
    type: Optional[str] = None
    answer: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_ok(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in {"NUMERIC", "SHORT_ANSWER", "CODE", "SELF_REFLECTION", "ACTION_CHECKLIST"}:
            raise ValueError(f"unsupported exercise type '{value}'")
        return normalized


class LessonSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str
    description: Optional[str] = None
    order: int = 0
    hours_estimated: float = 1.0
    topic: Optional[str] = None
    resources: list[ResourceSpec] = Field(default_factory=list)
    questions: list[QuestionSpec] = Field(default_factory=list)
    exercises: list[ExerciseSpec] = Field(default_factory=list)


class TopicSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: Optional[str] = None
    order: int = 0
    prerequisites: list[str] = Field(default_factory=list)
    learning_objective: Optional[str] = None
    mastery_criteria: list[str] = Field(default_factory=list)
    next_topic: Optional[str] = None
    fast_trackable: bool = True
    module: Optional[str] = None
    lessons: list[LessonSpec] = Field(default_factory=list)
    learning_track: Optional[str] = None
    depth_target: Optional[str] = None
    parallel_eligible: Optional[bool] = None
    estimated_minutes: Optional[int] = None
    domain_key: Optional[str] = None

    @field_validator("learning_track")
    @classmethod
    def track_ok(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        upper = value.upper()
        if upper not in LEARNING_TRACKS:
            raise ValueError(f"unsupported learning_track '{value}'")
        return upper

    @field_validator("depth_target")
    @classmethod
    def depth_ok(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        upper = value.upper()
        if upper not in DEPTH_TARGETS:
            raise ValueError(f"unsupported depth_target '{value}'")
        return upper


class ModuleSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: Optional[str] = None
    order: int = 0
    subject: Optional[str] = None
    topics: list[TopicSpec] = Field(default_factory=list)


class SubjectSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: Optional[str] = None
    order: int = 0
    modules: list[ModuleSpec] = Field(default_factory=list)


class LevelSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: Optional[str] = None
    order: int = 0
    subjects: list[SubjectSpec] = Field(default_factory=list)


class TrackSpec(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: Optional[str] = None
    order: int = 0
    levels: list[LevelSpec] = Field(default_factory=list)


class CurriculumManifest(BaseModel):
    schema_version: Literal[1] = 1
    kind: Literal["curriculum_manifest"] = "curriculum_manifest"
    origin: Literal["demo", "official"]
    track: TrackSpec

    def walk_topics(self) -> list[tuple[ModuleSpec, TopicSpec]]:
        pairs = []
        for level in self.track.levels:
            for subject in level.subjects:
                for module in subject.modules:
                    for topic in module.topics:
                        pairs.append((module, topic))
        return pairs


class CurriculumIndex(BaseModel):
    schema_version: Literal[1] = 1
    kind: Literal["curriculum_index"]
    origin: Literal["demo", "official"]
    files: list[str]


def load_manifest_dict(data: dict[str, Any]) -> CurriculumManifest:
    return CurriculumManifest.model_validate(data)

