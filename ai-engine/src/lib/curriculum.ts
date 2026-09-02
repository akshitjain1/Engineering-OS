export type UiStatus = "not_started" | "in_progress" | "completed" | "locked";

export type ProgressRatio = {
  completed: number;
  total: number;
  percent: number;
};

export type PrerequisiteItem = {
  name: string;
  complete: boolean;
  found: boolean;
};

export type LessonSummary = {
  id: number;
  title: string;
  description: string | null;
  topic_id: number;
  order_index: number;
  completion_status: Exclude<UiStatus, "locked">;
  hours_estimated: number;
};

export type TopicCompletion = {
  complete: boolean;
  learning_done: boolean;
  lessons_complete: boolean;
  resources_complete: boolean;
  exercises_complete: boolean;
  has_questions: boolean;
  assessment_ok: boolean | null;
  lesson_count: number;
};

export type AssessmentSummary = {
  score: number;
  correct: number;
  total: number;
  attempted: number;
  per_category: Record<string, number>;
  topic_id: number;
};

export type AssessmentQuestion = {
  id: number;
  prompt: string;
  options: string[];
  difficulty: string | null;
};

export type AssessmentPrevious = {
  question_id: number;
  prompt: string | null;
  selected: string;
  correct: boolean;
  explanation: string | null;
};

export type AssessmentSessionState = {
  session_id: number;
  topic_id: number;
  topic_name: string | null;
  status: "in_progress" | "completed";
  total: number;
  answered: number;
  current: AssessmentQuestion | null;
  previous: AssessmentPrevious | null;
  complete: boolean;
  summary: AssessmentSummary | null;
};

export type TopicNode = {
  id: number;
  slug?: string | null;
  name: string;
  description: string | null;
  learning_objective?: string | null;
  learning_track?: string | null;
  depth_target?: string | null;
  domain_key?: string | null;
  parallel_eligible?: boolean;
  study_contract?: Record<string, unknown> | null;
  domain?: string | null;
  pace_mode?: string | null;
  hours_estimated?: number | null;
  module_id: number;
  order_index: number;
  locked: boolean;
  lock_message: string | null;
  status: UiStatus;
  progress: ProgressRatio;
  prerequisites: PrerequisiteItem[];
  lessons: LessonSummary[];
  next_lesson_id: number | null;
  questions?: QuestionPublic[];
  exercises?: ExercisePublic[];
  implement?: ExercisePublic[];
  transfer?: ExercisePublic[];
  resources?: ResourcePublic[];
  resources_by_role?: {
    PRIMARY: ResourcePublic[];
    REFERENCE: ResourcePublic[];
    PRACTICE: ResourcePublic[];
    DEEP_DIVE: ResourcePublic[];
    OTHER?: ResourcePublic[];
  };
  mastery?: MasteryPublic;
  completion?: TopicCompletion;
  assessment?: AssessmentSummary | null;
  breadcrumb?: {
    track_id: number | null;
    subject_id: number | null;
    subject_name: string | null;
    module_id: number | null;
    module_name: string | null;
    topic_id: number;
    topic_name: string;
  };
  next_in_sequence?: { id: number; slug?: string | null; name: string } | null;
};

export type ModuleNode = {
  id: number;
  name: string;
  description: string | null;
  progress: ProgressRatio;
  topics: TopicNode[];
};

export type SubjectNode = {
  id: number;
  name: string;
  description: string | null;
  progress: ProgressRatio;
  modules: ModuleNode[];
};

export type LevelNode = {
  id: number;
  name: string;
  description: string | null;
  subjects: SubjectNode[];
};

export type TrackNode = {
  id: number;
  name: string;
  description: string | null;
  progress: ProgressRatio;
  levels: LevelNode[];
};

export type CurriculumTree = {
  tracks: TrackNode[];
  next: {
    track_id: number;
    track_name: string;
    module_id: number;
    module_name: string;
    topic_id: number;
    topic_name: string;
    lesson_id: number | null;
  } | null;
};

export type ResourcePublic = {
  id: number;
  title: string;
  url: string | null;
  resource_type: string;
  source_resource_type?: string | null;
  provider?: string | null;
  role?: string | null;
  section?: string | null;
  lecture?: string | null;
  video_id?: string | null;
  verification_status?: string | null;
  resource_status?: string | null;
  is_playlist?: boolean;
  exact?: boolean;
  exactness?: string | null;
  embeddable?: boolean;
  duration: number | null;
  /** Minutes this one source is expected to take. */
  estimated_minutes?: number | null;
  difficulty: string | null;
  description: string | null;
  official_unofficial: string;
  completion_status: string;
  completed: boolean;
};

export type MasteryPublic = {
  topic_id?: number | null;
  topic_slug?: string | null;
  status: string;
  mastery_score: number | null;
  confidence?: number | null;
  attempts?: number;
  evidence?: { source: string; category: string; score: number }[];
  pace_mode: string;
  next_review_at?: string | null;
  has_implementation_evidence?: boolean;
};

export type QuestionPublic = {
  id: number;
  question: string;
  options: string[];
  difficulty: string | null;
  attempt_count: number;
  last_answer: string | null;
  last_correct: boolean | null;
  correct?: boolean;
  answer?: string;
  explanation?: string | null;
};

export type ExercisePublic = {
  id: number;
  title: string;
  description: string | null;
  difficulty: string | null;
  completion_status: string;
  completed: boolean;
  exercise_type?: string | null;
  evaluated?: boolean;
  user_answer?: string | null;
  user_code?: string | null;
  user_explanation?: string | null;
  user_complexity?: string | null;
  correct_answer?: string | null;
};

export type ExerciseAnswerResult = ExercisePublic & {
  correct?: boolean | null;
  xp_awarded: number;
  evaluated: boolean;
};

export type LessonDetail = {
  id: number;
  title: string;
  description: string | null;
  topic_id: number;
  order_index: number;
  completion_status: Exclude<UiStatus, "locked">;
  hours_estimated: number;
  locked: boolean;
  lock_message: string | null;
  prerequisites: PrerequisiteItem[];
  breadcrumb: {
    module_id: number | null;
    module_name: string | null;
    topic_id: number;
    topic_name: string | null;
    lesson_id: number;
    lesson_title: string;
  };
  resources: ResourcePublic[];
  questions: QuestionPublic[];
  exercises: ExercisePublic[];
};
