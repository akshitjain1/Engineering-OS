"""PART O — prerequisite & parallel-learning intelligence tests.

Planner contract (verified against app/learning/service.py build_topic_views):
- TopicView.locked already encodes "incomplete OR blocked" computed upstream
  from the completion contract; prerequisites_locked() propagates blocking.
- prerequisite refs may be legacy strings or enhanced dicts — both supported.

Seeds the shared in-memory DB with a graph mirroring production wiring for
DSA early unlock, ML just-in-time math bridge, DL enforcement, CV-on-DL.
"""
import pytest

from app.db.session import Base, SessionLocal, engine
from app.db.models import CurriculumLesson, CurriculumTopic
from app.learning.planner import TopicView, prerequisites_locked, unlock_status


SEED_TOPICS = [
    # (slug, prereqs, unlocked?)
    ("cf-time-complexity-intro", [], True),
    ("java-loops", [], True),
    ("java-break-continue", ["java-loops"], True),
    ("java-method-basics", ["java-break-continue"], True),
    ("java-lambdas", [], False),          # deep-Java chain incomplete
    ("java-stream-pipeline", ["java-lambdas"], False),
    # DSA root — ENHANCED dict format:
    (
        "dsa-algorithmic-thinking",
        [
            {"slug": "cf-time-complexity-intro", "type": "REQUIRED"},
            {"slug": "java-method-basics", "type": "REQUIRED"},
        ],
        False,
    ),
    # ML bridge — LEGACY string format:
    (
        "ml-gradient-descent-intuition",
        ["ml-loss-intuition", "math-gradient-intuition", "math-derivatives"],
        False,
    ),
    ("ml-loss-intuition", [], True),
    ("math-gradient-intuition", [], False),
    ("math-functions", [], False),
    ("math-derivatives", ["math-functions"], False),
    ("ml-types-of-ml", ["ml-what-is-ml"], False),
    ("ml-what-is-ml", [], False),
    # DL chain + enforcement dict edge onto existing topic:
    ("dl-neuron-intuition", [], False),
    ("dl-perceptron", ["dl-neuron-intuition"], False),
    ("dl-nn-basics", [{"slug": "dl-perceptron", "type": "REQUIRED"}], False),
    ("dl-attention-intuition", [], False),
    ("dl-transformers-foundations", ["dl-attention-intuition"], False),
    ("dl-transformers-intro", [{"slug": "dl-transformers-foundations", "type": "REQUIRED"}], False),
    # CV builds on DL mechanics:
    ("cv-what-is-an-image", [], False),
    ("cv-traditional-filters", ["cv-what-is-an-image"], False),
    ("dl-feature-maps", [], False),
    ("cv-convolution-in-cv", ["cv-traditional-filters", "dl-feature-maps"], False),
]


@pytest.fixture(scope="module")
def db_topics():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)  # safe if a previous module dropped all
        existing = {t.slug for t in db.query(CurriculumTopic).all()}
        if not {"dsa-algorithmic-thinking", "cv-convolution-in-cv"} <= existing:
            for slug, prereqs, _unlocked in SEED_TOPICS:
                topic = CurriculumTopic(
                    slug=slug,
                    name=slug.replace("-", " ").title(),
                    module_id=1,
                    order_index=0,
                    prerequisites=prereqs,
                    estimated_minutes=20,
                )
                db.add(topic)
                db.flush()
                db.add(
                    CurriculumLesson(
                        slug=f"{slug}-lesson",
                        title=slug,
                        topic_id=topic.id,
                        order_index=0,
                        completion_status="not_started",
                    )
                )
            db.commit()
        rows = db.query(CurriculumTopic).all()
        # PURE DATA: immune to later drop_all() by other fixtures.
        return {t.slug: {'prerequisites': list(t.prerequisites or [])} for t in rows if t.slug}
    finally:
        db.close()


def _tv(slug, prereqs, locked=False):
    return TopicView(
        id=abs(hash(slug)) % 100000,
        slug=slug,
        name=slug,
        locked=locked,
        lessons_complete=False,
        domain=slug.split("-")[0],
        track="P",
        prerequisite_slugs=prereqs,
    )


class TestPrereqFormatCompat:
    def test_old_string_format_required_and_satisfied(self):
        child = _tv("child", ["parent-a"])
        parent_done = _tv("parent-a", [])  # unlocked upstream == satisfied
        assert prerequisites_locked(child, [child, parent_done]) is False

    def test_old_string_format_blocks_when_parent_locked(self):
        child = _tv("child", ["parent-a"])
        parent_incomplete = _tv("parent-a", [], locked=True)
        assert prerequisites_locked(child, [child, parent_incomplete]) is True

    def test_new_object_format(self):
        child = _tv("child", [{"slug": "parent-a", "type": "REQUIRED"}])
        done = _tv("parent-a", [])
        todo = _tv("parent-a", [], locked=True)
        assert prerequisites_locked(child, [child, done]) is False
        assert prerequisites_locked(child, [child, todo]) is True

    def test_dict_refs_resolve_by_slug_not_str(self):
        """Regression guard: raw dicts must resolve via their 'slug' key."""
        child = _tv("child", [{"slug": "p2", "type": "RECOMMENDED"}])
        p2_locked = _tv("p2", [], locked=True)
        assert prerequisites_locked(child, [child, p2_locked]) is False  # RECOMMENDED never blocks

        req_child = _tv("req-child", [{"slug": "p3", "type": "REQUIRED"}])
        p3_locked = _tv("p3", [], locked=True)
        assert prerequisites_locked(req_child, [req_child, p3_locked]) is True

    def test_mixed_formats_in_one_list(self):
        child = _tv("child", ["p1", {"slug": "p2", "type": "RECOMMENDED"}])
        p1_done = _tv("p1", [])
        p2_todo = _tv("p2", [])
        assert prerequisites_locked(child, [child, p1_done, p2_todo]) is False

    def test_recommended_does_not_block_even_if_locked(self):
        child = _tv("child", [{"slug": "rec", "type": "RECOMMENDED"}])
        rec_locked = _tv("rec", [], locked=True)
        assert prerequisites_locked(child, [child, rec_locked]) is False

    def test_awareness_safe_does_not_block_even_if_locked(self):
        child = _tv("child", [{"slug": "aw", "type": "AWARENESS_SAFE"}])
        aw_locked = _tv("aw", [], locked=True)
        assert prerequisites_locked(child, [child, aw_locked]) is False

    def test_unknown_prereq_locks_topic(self):
        child = _tv("child", ["nonexistent-topic"])
        assert prerequisites_locked(child, [child]) is True

    def test_real_seed_accepts_both_formats(self, db_topics):
        pool = [_tv(s, t['prerequisites']) for s, t in db_topics.items()]
        gdi = _tv("ml-gradient-descent-intuition", db_topics["ml-gradient-descent-intuition"]['prerequisites'])
        dsa = _tv("dsa-algorithmic-thinking", db_topics["dsa-algorithmic-thinking"]['prerequisites'])
        pool += [gdi, dsa]
        # Must not raise regardless of ref format:
        assert isinstance(prerequisites_locked(gdi, pool), bool)
        assert isinstance(prerequisites_locked(dsa, pool), bool)


class TestDsaEarlyUnlock:
    def test_dsa_needs_only_java_methods_not_full_java(self, db_topics):
        dsa = db_topics["dsa-algorithmic-thinking"]
        slugs = {
            ref if isinstance(ref, str) else ref.get("slug")
            for ref in (dsa['prerequisites'])
        }
        assert "java-method-basics" in slugs
        for deep in ("java-stream-pipeline", "java-lambdas"):
            assert deep not in slugs

    def test_dsa_unlocks_before_deep_java_chain_completes(self, db_topics):
        views = {}
        for s, t in db_topics.items():
            # Completed chain: cf-tcx + loops->break-continue->methods.
            # Deep Java (lambdas->streams) remains locked.
            unlocked = {
                "cf-time-complexity-intro",
                "java-loops",
                "java-break-continue",
                "java-method-basics",
                # ML bridge ancestors irrelevant here but keep them unlocked:
                "ml-loss-intuition",
            }
            views[s] = _tv(s, t['prerequisites'], locked=(s not in unlocked) and s != "dsa-algorithmic-thinking")
        views["cf-time-complexity-intro"].lessons_complete = True
        views["java-method-basics"].lessons_complete = True
        assert unlock_status(views["dsa-algorithmic-thinking"], list(views.values()))
        # Deep Java still blocked behind its incomplete lambda chain:
        assert unlock_status(views["java-stream-pipeline"], list(views.values())) is False


class TestMlBridgeJustInTime:
    def test_gradient_descent_requires_math_bridge_not_whole_domain(self, db_topics):
        ml = db_topics["ml-gradient-descent-intuition"]
        reqs = [
            ref if isinstance(ref, str) else ref.get("slug")
            for ref in (ml['prerequisites'])
        ]
        assert "math-derivatives" in reqs
        assert len(reqs) <= 5

    def test_math_functions_is_jit_dependency_only_of_derivatives(self, db_topics):
        mf = db_topics["math-functions"]
        assert mf['prerequisites'] in ([], None)
        dependents = []
        for s, t in db_topics.items():
            reqs = [r if isinstance(r, str) else r.get("slug") for r in (t['prerequisites'])]
            if "math-functions" in reqs:
                dependents.append(s)
        assert set(dependents) <= {"math-derivatives"}

    def test_dl_nn_basics_blocked_until_perceptron_chain_ready(self, db_topics):
        views = [_tv(s, t['prerequisites']) for s, t in db_topics.items()]
        by_slug = {v.slug: v for v in views}
        # Unlock everything except the neuron->perceptron segment:
        for v in views:
            if v.slug in {"dl-perceptron", "dl-nn-basics"}:
                continue
            by_slug[v.slug].locked = True if False else v.locked
        by_slug["dl-neuron-intuition"].locked = False
        by_slug["dl-perceptron"].locked = True  # perceptron itself not done yet
        nn = next(v for v in views if v.slug == "dl-nn-basics")
        assert unlock_status(nn, views) is False

        by_slug["dl-perceptron"].locked = False  # now ready
        assert unlock_status(nn, views) is True

    def test_transformers_intro_enforced_on_foundations(self, db_topics):
        ti = db_topics["dl-transformers-intro"]
        reqs = {
            ref if isinstance(ref, str) else ref.get("slug") for ref in (ti['prerequisites'])
        }
        assert "dl-transformers-foundations" in reqs

    def test_cv_convolution_requires_dl_feature_maps(self, db_topics):
        conv = db_topics["cv-convolution-in-cv"]
        reqs = {
            ref if isinstance(ref, str) else ref.get("slug") for ref in (conv['prerequisites'])
        }
        assert "dl-feature-maps" in reqs


class TestGraphAcyclicity:
    def test_seeded_graph_acyclic(self, db_topics):
        graph = {}
        for s, t in db_topics.items():
            deps = {
                ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))
                for ref in (t['prerequisites'])
            }
            deps.discard(None)
            deps.discard(s)
            graph[s] = deps
        color = {s: 0 for s in graph}

        def has_cycle(node) -> bool:
            color[node] = 1
            for dep in graph.get(node, ()):
                if dep not in color:
                    continue
                if color[dep] == 1:
                    return True
                if color[dep] == 0 and has_cycle(dep):
                    return True
            color[node] = 2
            return False

        for slug in list(graph):
            if color[slug] == 0:
                assert not has_cycle(slug)

    def test_seed_prereq_targets_exist(self, db_topics):
        missing = []
        for s, t in db_topics.items():
            for ref in t['prerequisites']:
                dep = ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))
                if dep and dep not in db_topics:
                    missing.append((s, dep))
        assert missing == []


class TestParallelSafety:
    def test_ml_types_is_light_awareness_topic(self, db_topics):
        t = db_topics["ml-types-of-ml"]
        reqs = [ref if isinstance(ref, str) else ref.get("slug") for ref in (t['prerequisites'])]
        assert reqs == ["ml-what-is-ml"]
