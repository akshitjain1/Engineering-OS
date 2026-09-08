"""Guards for the content defects that shipped, so they cannot ship twice.

Three defects were found in the curriculum content and fixed:

1. 94 questions were template filler: "Core idea of {TOPIC}?" with the
   distractors "A vague buzzword", "Irrelevant outside interviews" and
   "Replaces prerequisites".
2. One set of eleven generic dynamic-programming questions was attached to
   all twelve DP topics, so a Knapsack page quizzed you on memoisation.
3. 57 resources pointed at raw.githubusercontent.com source files, which a
   browser renders as plain text with the maths and figures stripped.

Each test below fails if the corresponding defect comes back. The bank tests
run offline against the files actually committed, so a bad bank cannot reach
the database via a passing test run.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.content.audit_resource_links import LinkCheck, classify
from app.content.question_bank import (
    normalise_prompt,
    parse_bank,
    validate_bank,
)
from app.content.repair_resource_links import rendered_url

BACKEND = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = BACKEND / "content" / "questions"


def _bank(questions, topic="cv-what-is-an-image"):
    return {
        "schema_version": 1,
        "kind": "question_bank",
        "module": "mod-test",
        "topics": [{"topic": topic, "questions": questions}],
    }


def _question(**overrides):
    base = {
        "id": "q-example",
        "prompt": "Which axis of a NumPy image array holds the colour channels?",
        "options": ["axis 2, the last one", "axis 0, the row axis", "axis 1, the column axis", "axis 3, a spare axis"],
        "answer": "axis 2, the last one",
        "explanation": (
            "Channels are last in RGB order, so axis 2 is correct, while axis 0 indexes rows "
            "and axis 1 indexes columns; there is no axis 3 on a colour image."
        ),
        "difficulty": "beginner",
    }
    base.update(overrides)
    return base


def _spread(questions):
    """Give each question a distinct id and prompt so only the trait under test fails."""
    out = []
    for index, question in enumerate(questions):
        copy = dict(question)
        copy["id"] = f"{copy['id']}-{index}"
        copy["prompt"] = f"{copy['prompt'][:-1]} (variant {index})?"
        out.append(copy)
    return out


# --------------------------------------------------------------------------
# Defect 1: template filler
# --------------------------------------------------------------------------


def test_the_filler_question_that_shipped_is_rejected():
    """The exact question and distractors that were in the database."""
    filler = {
        "id": "dl-nn-basics-core",
        "prompt": "Core idea of Neural network basics?",
        "options": [
            "A vague buzzword",
            "Explain layers, activations, and forward pass.",
            "Irrelevant outside interviews",
            "Replaces prerequisites",
        ],
        "answer": "Explain layers, activations, and forward pass.",
        "explanation": "It is the core idea of the topic, which you are expected to be able to state.",
        "difficulty": "beginner",
    }
    errors = validate_bank(parse_bank(_bank(_spread([filler] * 4))))
    assert errors, "the filler question that shipped must not validate"
    joined = " ".join(errors)
    assert "template" in joined or "banned filler" in joined


def test_answer_guessable_from_option_length_is_rejected():
    """Three curt distractors beside one long correct answer teaches test-taking."""
    lopsided = _question(
        options=[
            "axis 2, because channels are stored last in standard RGB ordering on load",
            "axis 0",
            "axis 1",
            "axis 3",
        ],
        answer="axis 2, because channels are stored last in standard RGB ordering on load",
    )
    errors = validate_bank(parse_bank(_bank(_spread([lopsided] * 4))))
    assert any("length" in error for error in errors)


def test_thin_explanation_is_rejected():
    thin = _question(explanation="Because it is axis 2.")
    errors = validate_bank(parse_bank(_bank(_spread([thin] * 4))))
    assert any("explanation" in error for error in errors)


def test_answer_must_be_one_of_the_options():
    mismatched = _question(answer="axis two, the last one")
    errors = validate_bank(parse_bank(_bank(_spread([mismatched] * 4))))
    assert any("answer is not one of the options" in error for error in errors)


def test_a_topic_needs_more_than_one_question():
    errors = validate_bank(parse_bank(_bank([_question()])))
    assert any("needs at least" in error for error in errors)


# --------------------------------------------------------------------------
# Defect 2: one question set spread across sibling topics
# --------------------------------------------------------------------------


def test_the_same_prompt_on_two_topics_is_rejected():
    """This is the DP defect stated directly: twelve topics, one question set."""
    shared = _spread([_question()] * 4)
    data = {
        "schema_version": 1,
        "kind": "question_bank",
        "module": "mod-dsa-dp",
        "topics": [
            {"topic": "dsa-dp-knapsack", "questions": shared},
            {"topic": "dsa-dp-grid", "questions": [dict(q, id=q["id"] + "-b") for q in shared]},
        ],
    }
    errors = validate_bank(parse_bank(data))
    assert any("already used by topic" in error for error in errors)


def test_a_prompt_already_stored_against_another_topic_is_rejected():
    """Re-importing must not move a sibling's question onto this topic."""
    question = _question()
    errors = validate_bank(
        parse_bank(_bank(_spread([question] * 4), topic="dsa-dp-knapsack")),
        prompts_elsewhere={normalise_prompt(_spread([question] * 4)[0]["prompt"]): "dsa-dp-grid"},
    )
    assert any("already stored against topic" in error for error in errors)


def test_a_well_formed_bank_validates():
    """The gates must not be so strict that good content cannot pass them."""
    assert validate_bank(parse_bank(_bank(_spread([_question()] * 4)))) == []


# --------------------------------------------------------------------------
# Every bank committed to the repository stays valid
# --------------------------------------------------------------------------


def _bank_files() -> list[Path]:
    if not QUESTIONS_DIR.exists():
        return []
    return sorted(p for p in QUESTIONS_DIR.glob("*.yaml") if not p.name.startswith("_"))


@pytest.mark.parametrize("path", _bank_files(), ids=lambda p: p.name)
def test_committed_question_bank_is_valid(path: Path):
    """Runs offline against the files on disk, so a bad bank fails the suite."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    errors = validate_bank(parse_bank(data, path.name))
    assert errors == [], "\n".join(errors[:20])


def test_no_prompt_is_shared_between_two_bank_files():
    """The cross-topic duplication check has to hold across modules too."""
    seen: dict[str, str] = {}
    clashes: list[str] = []
    for path in _bank_files():
        bank = parse_bank(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, path.name)
        for topic in bank.topics:
            for question in topic.questions:
                key = normalise_prompt(question.prompt)
                if key in seen and seen[key] != topic.topic_slug:
                    clashes.append(f"{topic.topic_slug} reuses a prompt from {seen[key]}")
                seen.setdefault(key, topic.topic_slug)
    assert clashes == [], "\n".join(clashes[:20])


# --------------------------------------------------------------------------
# Defect 3: resources that load as source text, and link classification
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/image-augmentation.md",
            "https://d2l.ai/chapter_computer-vision/image-augmentation.html",
        ),
        (
            "https://raw.githubusercontent.com/huggingface/course/main/chapters/en/chapter2/4.mdx",
            "https://huggingface.co/learn/llm-course/chapter2/4",
        ),
        (
            "https://raw.githubusercontent.com/pytorch/tutorials/main/beginner_source/basics/tensorqs_tutorial.py",
            "https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html",
        ),
    ],
)
def test_raw_source_urls_map_to_a_readable_page(raw: str, expected: str):
    assert rendered_url(raw) == expected


def test_an_already_readable_url_is_left_alone():
    assert rendered_url("https://d2l.ai/chapter_computer-vision/fcn.html") is None


def test_plain_text_response_is_flagged():
    check = LinkCheck(
        url="https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_x/y.md",
        status=200,
        final_url="https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_x/y.md",
        content_type="text/plain",
    )
    assert "PLAIN_TEXT" in classify(check, "D2L.ai")


def test_a_missing_page_is_dead_but_an_unanswered_request_is_not():
    """A timeout is not evidence a page is gone, and must not trigger a repair."""
    missing = LinkCheck(url="https://example.com/gone", status=404, error="HTTP 404")
    assert classify(missing, None) == ["DEAD"]

    timed_out = LinkCheck(url="https://www.gnu.org/software/bash/manual/", error="TimeoutError")
    assert classify(timed_out, "GNU") == ["UNREACHABLE"]


def test_bot_protection_is_not_reported_as_a_broken_link():
    """LeetCode answers 403 to every non-browser request; 244 rows looked dead."""
    check = LinkCheck(
        url="https://leetcode.com/problems/two-sum/",
        status=403,
        final_url="https://leetcode.com/problems/two-sum/",
        error="HTTP 403",
    )
    assert classify(check, "LeetCode") == ["BOT_PROTECTED"]


def test_provider_must_match_the_host_serving_the_page():
    lying = LinkCheck(
        url="https://raw.githubusercontent.com/x/y/z.md",
        status=200,
        final_url="https://raw.githubusercontent.com/x/y/z.md",
        content_type="text/plain",
    )
    assert "PROVIDER_MISMATCH" in classify(lying, "scikit-learn")

    honest = LinkCheck(
        url="https://scikit-learn.org/stable/modules/preprocessing.html",
        status=200,
        final_url="https://scikit-learn.org/stable/modules/preprocessing.html",
        content_type="text/html",
    )
    assert classify(honest, "scikit-learn") == []


def test_anthropic_docs_host_is_recognised():
    """platform.claude.com is Anthropic's docs host, not a mismatch."""
    check = LinkCheck(
        url="https://platform.claude.com/docs/en/build-with-claude/context-windows",
        status=200,
        final_url="https://platform.claude.com/docs/en/build-with-claude/context-windows",
        content_type="text/html",
    )
    assert classify(check, "Anthropic") == []


# --------------------------------------------------------------------------
# Study guidance: the Focus list has to be readable
# --------------------------------------------------------------------------


def test_focus_concepts_show_words_not_machine_slugs():
    """The "Focus" list was rendering concept slugs straight from the registry.

    A learner opening the DP mindset topic read
    ``dsa-dp-mindset-recognize-overlapping-subproblems-and-op`` -- a slug,
    truncated mid-word. The registry carries a human sentence per concept, and
    that is what belongs on the page.
    """
    from types import SimpleNamespace

    from app.main import _focus_concepts

    audit = SimpleNamespace(
        required_concepts=[
            "dsa-dp-mindset-dp-mindset",
            "dsa-dp-mindset-recognize-overlapping-subproblems-and-op",
        ]
    )
    focus = _focus_concepts("dsa-dp-mindset", audit)

    assert focus, "a topic with required concepts must show some guidance"
    for item in focus:
        assert " " in item, f"{item!r} is a slug, not a sentence"
        assert not item.startswith("dsa-dp-mindset-"), f"{item!r} still leaks the slug prefix"


def test_focus_concepts_drop_the_understand_wrapper_duplicate():
    """Generated contracts hold the same objective twice, once wrapped.

    ``Understand Foo: <objective>`` and ``<objective>`` say the same thing, so
    listing both is noise that reads like filler even when the objective is real.
    """
    from types import SimpleNamespace

    from app.main import _focus_concepts

    audit = SimpleNamespace(required_concepts=["be-auth-basics-auth-basics", "be-auth-basics-distinguish-authentication-vs-authorizat"])
    focus = _focus_concepts("be-auth-basics", audit)

    assert len(focus) == 1, f"expected the wrapper to be dropped, got {focus}"
    assert focus[0].lower().startswith("distinguish")


def test_focus_concepts_is_empty_without_an_audit():
    from app.main import _focus_concepts

    assert _focus_concepts("cv-what-is-an-image", None) == []


# --------------------------------------------------------------------------
# Every topic must answer the two questions the study contract promises
# --------------------------------------------------------------------------


def test_every_primary_resource_says_how_much_of_the_page_is_yours():
    """The topic page renders `section` as "Exact section: ...", a promise.

    104 primary resources used to store a string derived from the URL itself
    (`section: Git-Basics-Recording-Changes-to-the-Repository` under a page of
    that name; `section: 0` under `weeks/0/`) and another 132 stored nothing.
    A primary must now either name a real part of the page, say to read the
    whole page, or admit it has no boundary loudly enough for the page to warn.
    """
    import sqlite3

    db = BACKEND / "dev.db"
    if not db.exists():
        pytest.skip("dev.db not present")

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    silent = [
        row["slug"]
        for row in conn.execute(
            """
            SELECT t.slug, r.section, r.exactness
              FROM curriculum_resources r
              JOIN curriculum_lessons l ON r.lesson_id = l.id
              JOIN curriculum_topics t ON l.topic_id = t.id
             WHERE UPPER(COALESCE(r.role,'')) = 'PRIMARY'
               AND (r.section IS NULL OR r.section = '')
               AND COALESCE(r.exactness,'') NOT IN ('MULTI_TOPIC', 'COLLECTION')
            """
        )
    ]
    conn.close()
    assert silent == [], f"{len(silent)} primary resource(s) silently unbounded: {silent[:10]}"


def test_section_that_merely_echoes_the_url_is_detected():
    """The rule that found those 104, kept so it cannot drift."""
    from app.content.repair_section_boundaries import boundary_from_title, echoes_url

    assert echoes_url(
        "Git-Basics-Recording-Changes-to-the-Repository",
        "https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository",
    )
    assert echoes_url("0", "https://cs50.harvard.edu/x/weeks/0/")
    assert echoes_url("command-line-environment", "https://missing.csail.mit.edu/2026/command-line-environment/")
    assert echoes_url("above; content inspection pending", "https://docs.opencv.org/4.x/da/df5/x.html")

    # A real boundary must survive.
    assert not echoes_url("The Convolutional Layer", "https://cs231n.github.io/convolutional-networks/")
    assert not echoes_url("FULL_SINGLE_PAGE", "https://d2l.ai/chapter_computer-vision/fcn.html")
    assert not echoes_url(None, "https://example.com/x")

    # A title that states the boundary is worth reading it out of.
    assert boundary_from_title("Abdul Bari Algorithms playlist - watch: Merge Sort") == "Merge Sort"
    assert boundary_from_title("GFG - Merge Sort") is None


def test_every_topic_has_focus_guidance():
    """The Focus panel is where a learner reads what to take from the page.

    57 newly added topics had no concept contract and so showed an empty
    panel; two more recorded their concepts as optional, which the payload was
    not reading. Both are fixed, and neither should regress.

    Checked against the registry rather than through a session, because the
    suite runs on an in-memory database with no curriculum in it.
    """
    import sqlite3

    from app.content.concept_contracts import get_topic_concepts

    db_path = BACKEND / "dev.db"
    if not db_path.exists():
        pytest.skip("dev.db not present")

    conn = sqlite3.connect(db_path)
    slugs = [row[0] for row in conn.execute("SELECT slug FROM curriculum_topics WHERE slug IS NOT NULL")]
    conn.close()

    empty = []
    for slug in slugs:
        entry = get_topic_concepts(slug)
        if entry is None or not (entry.required or entry.optional):
            empty.append(slug)
    assert empty == [], f"{len(empty)} topic(s) would show an empty Focus list: {empty[:10]}"


def test_focus_concepts_prefer_required_then_fall_back_to_optional():
    """Two topics record concepts as optional so coverage does not gate them.

    That is a readiness decision, not a reason to render an empty panel.
    """
    from types import SimpleNamespace

    from app.main import _focus_concepts

    audit = SimpleNamespace(required_concepts=[])
    focus = _focus_concepts("cv-efficientnet-awareness", audit)
    assert focus, "a topic with only optional concepts must still show them"
    assert any("scaling" in item.lower() for item in focus)


def test_focus_guidance_never_reintroduces_the_boilerplate():
    """"Explain X in your own words" is not guidance; it is the filler shape."""
    from app.content.concepts_from_mastery import mastery_criteria

    description = (
        "Some topic.\n\nObjective: Do a thing.\n\nMastery:\n"
        "- Explain Deep Learning awareness in your own words.\n"
        "- Complete the mapped practice checklist.\n"
        "- Score >= 80% on the topic questions.\n"
    )
    assert mastery_criteria(description) == []

    real = (
        "Data leakage.\n\nObjective: Detect it.\n\nMastery:\n"
        "- Point at the exact line in a script that leaks when a scaler is fit before splitting.\n"
        "- State the rule that prevents preprocessing leakage in one sentence.\n"
    )
    assert len(mastery_criteria(real)) == 2


def test_dry_run_import_writes_nothing(tmp_path, monkeypatch):
    """`--dry-run` must not reach the database.

    Two authoring agents reported seeing their questions in the database
    before their own dry run finished, and asked whether the rollback was
    holding. It was -- a parallel process had imported the whole directory --
    but "probably fine" is not an answer for a flag whose entire purpose is to
    be safe to run. This proves it.
    """
    import yaml

    from app.content import import_questions as importer
    from app.db.models import CurriculumLesson, CurriculumModule, CurriculumSubject
    from app.db.models import CurriculumLevel, CurriculumTopic, CurriculumTrack, LessonQuestion
    from app.db.session import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        track = CurriculumTrack(slug="t-dry", name="Dry Run Track", order_index=0)
        level = CurriculumLevel(slug="l-dry", name="Dry Run Level", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(
            slug="s-dry", name="Dry Run Subject", track_id=track.id, level_id=level.id
        )
        db.add(subject)
        db.flush()
        module = CurriculumModule(slug="m-dry", name="Dry Run Module", subject_id=subject.id)
        db.add(module)
        db.flush()
        topic = CurriculumTopic(slug="dry-run-topic", name="Dry Run Topic", module_id=module.id)
        db.add(topic)
        db.flush()
        db.add(CurriculumLesson(slug="dry-run-topic-core", title="Dry Run Topic", topic_id=topic.id))
        db.commit()
        before = db.query(LessonQuestion).count()
    finally:
        db.close()

    bank = {
        "schema_version": 1,
        "kind": "question_bank",
        "module": "m-dry",
        "topics": [{"topic": "dry-run-topic", "questions": _spread([_question()] * 4)}],
    }
    path = tmp_path / "mod-dry.yaml"
    path.write_text(yaml.safe_dump(bank, sort_keys=False), encoding="utf-8")

    report = importer.import_questions([path], dry_run=True)
    assert report.errors == [], report.errors
    assert report.created == 4, "the dry run should still report what it would do"

    db = SessionLocal()
    try:
        assert db.query(LessonQuestion).count() == before, "a dry run wrote to the database"
    finally:
        db.close()
