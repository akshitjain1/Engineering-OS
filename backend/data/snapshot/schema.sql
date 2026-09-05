CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE assessment_sessions (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	topic_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	question_ids JSON, 
	current_index INTEGER NOT NULL, 
	answers JSON, 
	started_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	summary JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(topic_id) REFERENCES curriculum_topics (id)
);

CREATE TABLE curriculum_lessons (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	title VARCHAR(100) NOT NULL, 
	description TEXT, 
	topic_id INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	completion_status VARCHAR(20) NOT NULL, 
	mastery_status VARCHAR(20) NOT NULL, 
	confidence FLOAT NOT NULL, 
	hours_estimated FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(topic_id) REFERENCES curriculum_topics (id)
);

CREATE TABLE curriculum_levels (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	name VARCHAR(50) NOT NULL, 
	description TEXT, 
	order_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE curriculum_modules (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	subject_id INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subject_id) REFERENCES curriculum_subjects (id)
);

CREATE TABLE curriculum_resources (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	title VARCHAR(200) NOT NULL, 
	url VARCHAR(500) NOT NULL, 
	resource_type VARCHAR(50) NOT NULL, 
	provider VARCHAR(100), 
	topic VARCHAR(100), 
	duration FLOAT, 
	difficulty VARCHAR(20), 
	description TEXT, 
	official_unofficial VARCHAR(10) NOT NULL, 
	order_index INTEGER NOT NULL, 
	completion_status VARCHAR(20) NOT NULL, 
	lesson_id INTEGER, 
	role VARCHAR(20), 
	section VARCHAR(200), 
	lecture VARCHAR(200), 
	video_id VARCHAR(40), 
	verification_status VARCHAR(20) NOT NULL, 
	estimated_minutes INTEGER, 
	required_concepts_covered JSON, 
	exactness VARCHAR(20), 
	notes TEXT, estimate_confidence VARCHAR(10), estimate_method VARCHAR(40), verification_evidence TEXT, last_verified_at VARCHAR(40), learner_visible BOOLEAN DEFAULT 1, visibility_class VARCHAR(40), boundary_type VARCHAR(40), start_boundary VARCHAR(200), end_boundary VARCHAR(200), start_timestamp VARCHAR(20), end_timestamp VARCHAR(20), 
	PRIMARY KEY (id), 
	FOREIGN KEY(lesson_id) REFERENCES curriculum_lessons (id)
);

CREATE TABLE curriculum_subjects (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	track_id INTEGER NOT NULL, 
	level_id INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(track_id) REFERENCES curriculum_tracks (id), 
	FOREIGN KEY(level_id) REFERENCES curriculum_levels (id)
);

CREATE TABLE curriculum_topics (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	module_id INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	prerequisites JSON, 
	fast_trackable BOOLEAN NOT NULL, learning_track VARCHAR(20) DEFAULT 'CORE' NOT NULL, depth_target VARCHAR(30) DEFAULT 'WORKING_KNOWLEDGE' NOT NULL, parallel_eligible BOOLEAN DEFAULT 0 NOT NULL, estimated_minutes INTEGER, domain_key VARCHAR(60), learning_minutes INTEGER, practice_minutes INTEGER, implementation_minutes INTEGER, revision_minutes INTEGER, total_training_minutes INTEGER, topic_type VARCHAR(30) DEFAULT 'LEARNABLE', 
	PRIMARY KEY (id), 
	FOREIGN KEY(module_id) REFERENCES curriculum_modules (id)
);

CREATE TABLE curriculum_tracks (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	order_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE daily_plan_items (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	plan_date VARCHAR(16) NOT NULL, 
	position INTEGER NOT NULL, 
	activity_type VARCHAR(20) NOT NULL, 
	title VARCHAR(240) NOT NULL, 
	subtitle VARCHAR(240), 
	why TEXT, 
	how TEXT, 
	topic_id INTEGER, 
	topic_slug VARCHAR(160), 
	domain VARCHAR(40), 
	resource_id INTEGER, 
	resource_title VARCHAR(300), 
	resource_provider VARCHAR(120), 
	resource_url TEXT, 
	resource_kind VARCHAR(40), 
	planned_minutes INTEGER NOT NULL, 
	actual_minutes INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	started_at DATETIME, 
	completed_at DATETIME, 
	note TEXT, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_day_item_position UNIQUE (user_id, plan_date, position), 
	FOREIGN KEY(topic_id) REFERENCES curriculum_topics (id), 
	FOREIGN KEY(resource_id) REFERENCES curriculum_resources (id)
);

CREATE TABLE daily_plans (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	plan_date VARCHAR(16) NOT NULL, 
	budget_minutes INTEGER NOT NULL, 
	goal VARCHAR(200) NOT NULL, 
	items JSON, 
	generated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_daily_plan_user_date UNIQUE (user_id, plan_date)
);

CREATE TABLE day_journals (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	entry_date VARCHAR(16) NOT NULL, 
	learned TEXT, 
	struggled TEXT, 
	tomorrow TEXT, 
	minutes_logged INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, built TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_day_journal UNIQUE (user_id, entry_date)
);

CREATE TABLE diagnostic_answers (
	id INTEGER NOT NULL, 
	session_id INTEGER NOT NULL, 
	question_id VARCHAR(80) NOT NULL, 
	payload JSON, 
	score FLOAT, 
	submitted_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_diagnostic_answer UNIQUE (session_id, question_id), 
	FOREIGN KEY(session_id) REFERENCES diagnostic_sessions (id)
);

CREATE TABLE diagnostic_sessions (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	question_ids JSON, 
	current_index INTEGER NOT NULL, 
	started_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	summary JSON, 
	PRIMARY KEY (id)
);

CREATE TABLE dsa_topics (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	pattern VARCHAR(50), 
	difficulty VARCHAR(20), 
	source VARCHAR(200), 
	url VARCHAR(500), 
	solution_notes TEXT, 
	attempt_count INTEGER NOT NULL, 
	time_taken FLOAT NOT NULL, 
	solved_status BOOLEAN NOT NULL, 
	revision_status VARCHAR(20) NOT NULL, 
	last_attempted DATETIME, 
	next_revision DATETIME, 
	personal_notes TEXT, 
	difficulty_level VARCHAR(20), 
	PRIMARY KEY (id)
);

CREATE TABLE engineering_projects (id INTEGER PRIMARY KEY, slug VARCHAR(160) NOT NULL, title VARCHAR(200) NOT NULL, goal TEXT, level INTEGER NOT NULL DEFAULT 1, difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner', estimated_hours FLOAT NOT NULL DEFAULT 2.0, prerequisites JSON, concepts_applied JSON, milestones JSON, deliverable TEXT, order_index INTEGER NOT NULL DEFAULT 0);

CREATE TABLE learning_activities (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	local_date VARCHAR(16) NOT NULL, 
	activity_type VARCHAR(40) NOT NULL, 
	minutes INTEGER NOT NULL, 
	source VARCHAR(80), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE lesson_exercises (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	difficulty VARCHAR(20), 
	topic VARCHAR(100), 
	completion_status VARCHAR(20) NOT NULL, 
	solution_notes TEXT, 
	time_taken FLOAT, 
	attempted_at DATETIME, 
	lesson_id INTEGER NOT NULL, 
	exercise_type VARCHAR(20) NOT NULL, 
	correct_answer TEXT, 
	user_answer TEXT, 
	user_code TEXT, 
	user_explanation TEXT, 
	user_complexity VARCHAR(20), 
	evaluated BOOLEAN NOT NULL, destination_type VARCHAR(40), destination_url VARCHAR(500), quantity INTEGER, concepts_required JSON, practice_instructions TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lesson_id) REFERENCES curriculum_lessons (id)
);

CREATE TABLE lesson_questions (
	id INTEGER NOT NULL, 
	slug VARCHAR(160), 
	question TEXT NOT NULL, 
	answer TEXT, 
	explanation TEXT, 
	difficulty VARCHAR(20), 
	topic VARCHAR(100), 
	source VARCHAR(200), 
	mastery_requirement BOOLEAN NOT NULL, 
	lesson_id INTEGER NOT NULL, 
	options JSON, 
	last_answer TEXT, 
	attempt_count INTEGER NOT NULL, 
	last_correct BOOLEAN, 
	last_attempt_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lesson_id) REFERENCES curriculum_lessons (id)
);

CREATE TABLE mastery_evidence (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	topic_slug VARCHAR(160) NOT NULL, 
	source VARCHAR(40) NOT NULL, 
	category VARCHAR(40) NOT NULL, 
	score FLOAT NOT NULL, 
	payload JSON, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE revision_schedules (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	item_id INTEGER NOT NULL, 
	item_type VARCHAR(50) NOT NULL, 
	confidence FLOAT NOT NULL, 
	last_reviewed DATETIME, 
	next_review DATETIME NOT NULL, 
	review_interval INTEGER NOT NULL, retrieval_success_count INTEGER DEFAULT 0 NOT NULL, retrieval_fail_count INTEGER DEFAULT 0 NOT NULL, ease FLOAT DEFAULT 2.5 NOT NULL, importance FLOAT DEFAULT 1.0 NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_revision_user_item UNIQUE (user_id, item_id, item_type)
);

CREATE TABLE topic_mastery (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	topic_id INTEGER, 
	topic_slug VARCHAR(160) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	mastery_score FLOAT, 
	confidence FLOAT NOT NULL, 
	attempts INTEGER NOT NULL, 
	last_assessed_at DATETIME, 
	last_completed_at DATETIME, 
	next_review_at DATETIME, 
	evidence JSON, 
	pace_mode VARCHAR(20) NOT NULL, 
	has_implementation_evidence BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_mastery_user_slug UNIQUE (user_id, topic_slug), 
	FOREIGN KEY(topic_id) REFERENCES curriculum_topics (id)
);

CREATE TABLE user_progress (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	lesson_id INTEGER, 
	topic_id INTEGER, 
	dsa_topic_id INTEGER, 
	progress_state VARCHAR(20) NOT NULL, 
	mastery_status VARCHAR(20) NOT NULL, 
	xp_earned INTEGER NOT NULL, 
	last_activity_at DATETIME, 
	streak_days INTEGER NOT NULL, 
	total_streak_days INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lesson_id) REFERENCES curriculum_lessons (id), 
	FOREIGN KEY(topic_id) REFERENCES curriculum_topics (id), 
	FOREIGN KEY(dsa_topic_id) REFERENCES dsa_topics (id)
);

CREATE TABLE user_project_progress (id INTEGER PRIMARY KEY, user_id VARCHAR(50) NOT NULL DEFAULT 'akshit', project_id INTEGER NOT NULL REFERENCES engineering_projects(id), state VARCHAR(20) NOT NULL DEFAULT 'locked', started_at DATETIME, completed_at DATETIME, CONSTRAINT uq_user_project UNIQUE (user_id, project_id));

CREATE TABLE user_streaks (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	current_streak INTEGER NOT NULL, 
	longest_streak INTEGER NOT NULL, 
	last_learning_date VARCHAR(16), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_streak UNIQUE (user_id)
);

CREATE TABLE user_study_settings (id INTEGER PRIMARY KEY, user_id VARCHAR(50) NOT NULL DEFAULT 'akshit', weekday_capacity_minutes INTEGER NOT NULL DEFAULT 90, weekend_capacity_minutes INTEGER NOT NULL DEFAULT 180, timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata', revision_weighted BOOLEAN DEFAULT 0 NOT NULL, CONSTRAINT uq_user_study_settings UNIQUE (user_id));

CREATE TABLE user_xp (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	total_xp INTEGER NOT NULL, 
	level INTEGER NOT NULL, 
	xp_this_session INTEGER NOT NULL, 
	sessions_completed INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_xp_user_id UNIQUE (user_id)
);

CREATE TABLE xp_events (
	id INTEGER NOT NULL, 
	user_id VARCHAR(50) NOT NULL, 
	idempotency_key VARCHAR(200) NOT NULL, 
	amount INTEGER NOT NULL, 
	activity VARCHAR(80) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_xp_event_key UNIQUE (user_id, idempotency_key)
);

CREATE INDEX ix_assessment_sessions_id ON assessment_sessions (id);

CREATE INDEX ix_assessment_sessions_topic_id ON assessment_sessions (topic_id);

CREATE INDEX ix_assessment_sessions_user_id ON assessment_sessions (user_id);

CREATE INDEX ix_curriculum_lessons_id ON curriculum_lessons (id);

CREATE UNIQUE INDEX ix_curriculum_lessons_slug ON curriculum_lessons (slug);

CREATE INDEX ix_curriculum_levels_id ON curriculum_levels (id);

CREATE UNIQUE INDEX ix_curriculum_levels_slug ON curriculum_levels (slug);

CREATE INDEX ix_curriculum_modules_id ON curriculum_modules (id);

CREATE UNIQUE INDEX ix_curriculum_modules_slug ON curriculum_modules (slug);

CREATE INDEX ix_curriculum_resources_id ON curriculum_resources (id);

CREATE UNIQUE INDEX ix_curriculum_resources_slug ON curriculum_resources (slug);

CREATE INDEX ix_curriculum_subjects_id ON curriculum_subjects (id);

CREATE UNIQUE INDEX ix_curriculum_subjects_slug ON curriculum_subjects (slug);

CREATE INDEX ix_curriculum_topics_id ON curriculum_topics (id);

CREATE UNIQUE INDEX ix_curriculum_topics_slug ON curriculum_topics (slug);

CREATE INDEX ix_curriculum_tracks_id ON curriculum_tracks (id);

CREATE UNIQUE INDEX ix_curriculum_tracks_slug ON curriculum_tracks (slug);

CREATE INDEX ix_daily_plan_items_id ON daily_plan_items (id);

CREATE INDEX ix_daily_plan_items_plan_date ON daily_plan_items (plan_date);

CREATE INDEX ix_daily_plan_items_status ON daily_plan_items (status);

CREATE INDEX ix_daily_plan_items_topic_id ON daily_plan_items (topic_id);

CREATE INDEX ix_daily_plan_items_user_id ON daily_plan_items (user_id);

CREATE INDEX ix_daily_plans_id ON daily_plans (id);

CREATE INDEX ix_daily_plans_user_id ON daily_plans (user_id);

CREATE INDEX ix_day_item_user_date ON daily_plan_items (user_id, plan_date);

CREATE INDEX ix_day_journals_entry_date ON day_journals (entry_date);

CREATE INDEX ix_day_journals_id ON day_journals (id);

CREATE INDEX ix_day_journals_user_id ON day_journals (user_id);

CREATE INDEX ix_diagnostic_answers_id ON diagnostic_answers (id);

CREATE INDEX ix_diagnostic_sessions_id ON diagnostic_sessions (id);

CREATE INDEX ix_diagnostic_sessions_user_id ON diagnostic_sessions (user_id);

CREATE INDEX ix_dsa_topics_id ON dsa_topics (id);

CREATE UNIQUE INDEX ix_engineering_projects_slug ON engineering_projects (slug);

CREATE INDEX ix_learning_activities_id ON learning_activities (id);

CREATE INDEX ix_learning_activities_local_date ON learning_activities (local_date);

CREATE INDEX ix_learning_activities_user_id ON learning_activities (user_id);

CREATE INDEX ix_lesson_exercises_id ON lesson_exercises (id);

CREATE UNIQUE INDEX ix_lesson_exercises_slug ON lesson_exercises (slug);

CREATE INDEX ix_lesson_questions_id ON lesson_questions (id);

CREATE UNIQUE INDEX ix_lesson_questions_slug ON lesson_questions (slug);

CREATE INDEX ix_mastery_evidence_id ON mastery_evidence (id);

CREATE UNIQUE INDEX ix_mastery_evidence_register ON mastery_evidence (user_id, topic_slug, source, category);

CREATE INDEX ix_mastery_evidence_topic_slug ON mastery_evidence (topic_slug);

CREATE INDEX ix_mastery_evidence_user_id ON mastery_evidence (user_id);

CREATE INDEX ix_revision_schedules_id ON revision_schedules (id);

CREATE INDEX ix_revision_schedules_next_review ON revision_schedules (next_review);

CREATE INDEX ix_topic_mastery_id ON topic_mastery (id);

CREATE INDEX ix_topic_mastery_topic_slug ON topic_mastery (topic_slug);

CREATE INDEX ix_topic_mastery_user_id ON topic_mastery (user_id);

CREATE INDEX ix_user_progress_id ON user_progress (id);

CREATE INDEX ix_user_project_progress_user_id ON user_project_progress (user_id);

CREATE INDEX ix_user_streaks_id ON user_streaks (id);

CREATE INDEX ix_user_streaks_user_id ON user_streaks (user_id);

CREATE INDEX ix_user_study_settings_user_id ON user_study_settings (user_id);

CREATE INDEX ix_user_xp_id ON user_xp (id);

CREATE INDEX ix_user_xp_user_id ON user_xp (user_id);

CREATE INDEX ix_xp_events_id ON xp_events (id);

CREATE INDEX ix_xp_events_user_id ON xp_events (user_id);
