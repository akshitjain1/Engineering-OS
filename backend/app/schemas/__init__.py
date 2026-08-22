from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


# Curriculum schemas
class CurriculumTrackCreate(BaseModel):
    name: str
    description: str = ""
    order_index: int = 0


class CurriculumTrackResponse(BaseModel):
    id: int
    name: str
    description: str = ""
    order_index: int

    class Config:
        from_attributes = True


class CurriculumLevelResponse(BaseModel):
    id: int
    name: str
    description: str = ""
    order_index: int

    class Config:
        from_attributes = True


class CurriculumSubjectResponse(BaseModel):
    id: int
    name: str
    description: str = ""
    track_id: int
    level_id: int
    order_index: int

    class Config:
        from_attributes = True


class CurriculumModuleResponse(BaseModel):
    id: int
    name: str
    description: str = ""
    subject_id: int
    order_index: int

    class Config:
        from_attributes = True


class CurriculumTopicResponse(BaseModel):
    id: int
    name: str
    description: str = ""
    module_id: int
    order_index: int
    prerequisites: list = []
    fast_trackable: bool = True

    class Config:
        from_attributes = True


class CurriculumLessonResponse(BaseModel):
    id: int
    title: str
    description: str = ""
    topic_id: int
    order_index: int
    completion_status: str = "not_started"
    mastery_status: str = "not_started"
    confidence: float = 0.0
    hours_estimated: float = 1.0

    class Config:
        from_attributes = True


class CurriculumResourceResponse(BaseModel):
    id: int
    title: str
    url: str
    resource_type: str
    topic: str = ""
    duration: float = None
    difficulty: str = None
    description: str = ""
    official_unofficial: str = "official"
    order_index: int = 0
    completion_status: str = "not_started"

    class Config:
        from_attributes = True


# DSA schemas
class DSATopicCreate(BaseModel):
    name: str
    pattern: str = ""
    difficulty: str = ""
    source: str = ""
    url: str = ""


class DSATopicResponse(BaseModel):
    id: int
    name: str
    pattern: str = ""
    difficulty: str = ""
    source: str = ""
    url: str = ""
    solution_notes: str = ""
    attempt_count: int = 0
    time_taken: float = 0.0
    solved_status: bool = False
    revision_status: str = "not_started"
    last_attempted: Optional[datetime] = None
    next_revision: Optional[datetime] = None
    personal_notes: str = ""
    difficulty_level: str = ""

    class Config:
        from_attributes = True


# User Progress schemas
class UserProgressResponse(BaseModel):
    id: int
    user_id: str = "akshit"
    lesson_id: Optional[int] = None
    topic_id: Optional[int] = None
    dsa_topic_id: Optional[int] = None
    progress_state: str = "not_started"
    mastery_status: str = "not_started"
    xp_earned: int = 0
    last_activity_at: Optional[datetime] = None
    streak_days: int = 0
    total_streak_days: int = 0

    class Config:
        from_attributes = True


# User XP schemas
class UserXPResponse(BaseModel):
    id: int
    user_id: str = "akshit"
    total_xp: int = 0
    level: int = 1
    xp_this_session: int = 0
    sessions_completed: int = 0

    class Config:
        from_attributes = True


# Revision schemas
class RevisionScheduleResponse(BaseModel):
    id: int
    user_id: str = "akshit"
    item_id: int
    item_type: str
    confidence: float = 0.0
    last_reviewed: Optional[datetime] = None
    next_review: datetime
    review_interval: int = 1

    class Config:
        from_attributes = True


# XP Award schemas
class XPAward(BaseModel):
    amount: int
    activity: str