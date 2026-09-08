# Resource Link Integrity — First Live Audit (2026-09-08)

## Why this audit happened

The learner reported that the content and questions on a topic page "are not
related" to the topic being studied. That turned out to be accurate, and for
three separate reasons. This document records what was wrong, what was fixed,
and the tooling that now keeps it fixed.

The curriculum's whole promise is *open exactly this page and study it*. That
promise is only as good as the URLs — and until this audit, **nothing in the
repository had ever fetched one**. Every previous audit checked the database
against itself: whether a topic had a PRIMARY, whether a concept contract was
covered, whether a section boundary was recorded. All of that can pass while
the URL 404s.

## 1. What the audit found

`python -m app.content.audit_resource_links` fetches every mapped URL and
classifies the response. First run, over 764 distinct URLs behind 1,246
resource rows:

| Flag | Rows | Meaning |
| --- | --- | --- |
| DEAD | 261 | server answered, page is not there |
| PROVIDER_MISMATCH | 58 | recorded publisher is not the host serving it |
| PLAIN_TEXT | 57 | loads, but the browser shows source, not a page |
| REDIRECTED | 28 | still resolves, but the page has moved |

897 of 1,246 rows were clean.

### PLAIN_TEXT — the worst of it, and invisible to every prior check

57 resources pointed at `raw.githubusercontent.com`. Those URLs return
`Content-Type: text/plain`, so a browser shows the **markdown source**:
unrendered LaTeX, figure directives instead of figures, code blocks as
literal backticks. The pages were not broken, they were unreadable.

The concentration is what made this severe:

| Module | Affected | Of |
| --- | --- | --- |
| `mod-dl-core` | 29 | 32 |
| `mod-nlp-core` | 11 | 16 |
| `mod-cv` | 10 | 26 |

That is the AI curriculum — precisely the material the learner is working
through — served as source text. Every one of these had a published,
rendered equivalent that was simply not the URL stored.

### DEAD — mostly a false alarm, and one real fabrication

244 of the 261 dead rows were `leetcode.com` answering **403** to a
non-browser request. That is bot protection, not breakage. Reporting it as
dead would have prompted 244 pointless replacements, so the classifier now
separates `BOT_PROTECTED` from `DEAD`.

The 17 genuine failures included one worth recording carefully, because the
first conclusion drawn from it was wrong.

Nine rows pointed at `missing.csail.mit.edu/2026/01-shell/` and
`/2026/02-environment/`, both 404. The first repair pass concluded that no 2026
edition of Missing Semester existed and moved all nine rows to the 2020
lectures.

That was wrong. `missing.csail.mit.edu/2026/` is live, and the curriculum
already linked seven other 2026 pages. Only the two *slugs* were wrong: the
2026 edition names its lectures descriptively (`course-shell`,
`command-line-environment`) rather than numerically (`01-shell`). The nine rows
have since been pulled forward to the 2026 edition, and the correction is
recorded in `repair_resource_links.py` next to the entries that caused it.

The lesson generalises: a 404 tells you a URL is wrong, not what is wrong with
it. Inferring that a whole publication does not exist from two dead paths is a
bigger claim than the evidence supports, and it silently downgraded nine
topics to a six-year-old edition of a course that is still being taught.

### WRONG_PAGE — loads fine, wrong subject

The failure mode no status code catches. Two `d2l.ai` links redirected to the
**book's homepage**, so "open exactly this" landed the learner on a front page:

- `chapter_multilayer-perceptrons/multilayer-perceptrons.html` → homepage
  (the real page is `mlp.html`)
- `chapter_convolutional-modern/lenet.html` → homepage
  (LeNet is in `chapter_convolutional-neural-networks/`)

Others named one publisher and served another:

| Topic | Recorded as | Actually served |
| --- | --- | --- |
| `cv-transformations` | scikit-learn — Image preprocessing | d2l augmentation **source file** |
| `cv-image-tensors` | CS231n — Input volumes as tensors | a Kaggle CIFAR-10 walkthrough |
| `cv-efficientnet-awareness` | D2L — Network Design | the **ResNet** page, which does not discuss scaling |
| `math-vectors` | Khan Academy | `mathinsight.org`, which also timed out |

## 2. What was repaired

`python -m app.content.repair_resource_links` — **158 rows** over several
passes. Every replacement was fetched and its `<title>` read before being
written down, and the script re-verifies each one live before touching the
database.

| Class | Rows | Repair |
| --- | --- | --- |
| RENDERED | 55 | raw source → the published page |
| RELOCATED | 57 | moved or renamed URLs → the real location |
| WRONG_PAGE | 27 | loads, wrong subject → the right page |
| MISLABELLED | 14 | title or provider corrected to what the page actually is |
| CORRECTION | 10 | a repair of an earlier repair (see the Missing Semester note) |

Rendered-page mappings, all verified to resolve without redirect:

```
raw.githubusercontent.com/d2l-ai/d2l-en/master/{chapter}/{page}.md
  -> d2l.ai/{chapter}/{page}.html                                   (35 URLs)
raw.githubusercontent.com/huggingface/course/.../chapter{N}/{M}.mdx
  -> huggingface.co/learn/llm-course/chapter{N}/{M}                 (4 URLs)
raw.githubusercontent.com/pytorch/tutorials/.../basics/{x}.py
  -> docs.pytorch.org/tutorials/beginner/basics/{x}.html            (6 URLs)
raw.githubusercontent.com/mlflow/.../classic-ml/{x}/index.mdx
  -> mlflow.org/docs/latest/ml/{x}/                                 (2 URLs)
```

Two changes were deliberately **not** made, and the reasoning is recorded in
the repair module so it is not "corrected" later:

- `docs.opencv.org/4.x/...` redirects to the current patch release. `4.x` is
  OpenCV's alias for latest; pinning `4.13.0` would go stale on the next
  release, so the alias is the more correct thing to store.
- `docs.junit.org/current/user-guide/` likewise. Aliases now carry an
  explicit `alias=True` flag so the verifier expects the redirect.

After repair, a full re-audit of all 1,250 rows reports:

| Flag | Before | After |
| --- | --- | --- |
| DEAD | 261 | **0** |
| PLAIN_TEXT | 57 | **0** |
| PROVIDER_MISMATCH | 58 | **0** |
| REDIRECTED | 28 | 3 |
| BOT_PROTECTED | (counted as DEAD) | 258 |
| UNREACHABLE | (counted as DEAD) | 4 |

The 3 remaining redirects are the deliberate "latest" aliases described above.
The 4 unreachable are three `gnu.org` Bash manual pages that this machine
cannot reach, an MIT OpenCourseWare redirect this client cannot follow, and
Sutton & Barto's PDF, which is `http://`-only because its host serves a
self-signed certificate. None of those is a wrong mapping.

### Link evidence is now recorded per row

`--record` stamps every resource row with `last_verified_at` and a
`verification_evidence.link_check` entry holding the HTTP status, the URL
landed on and the page title read from it. All 1,250 rows carry it.

This is deliberately kept apart from `verification_status`. A fetch establishes
that a URL is live and which page it serves. It cannot establish that the page
covers a topic's required concepts, which is what `VERIFIED_COVERAGE` asserts.
Conflating the two is how "NEEDS_REVIEW" came to read as "avoid this topic"
across the entire computer-vision curriculum — see section 5.

## 3. Study guidance was rendering machine slugs

Separate from the URLs, and the second reason the content felt unrelated.

The topic page shows a **Focus** list. It was populated from
`audit.required_concepts`, which holds concept *slugs*, because coverage is
computed by set arithmetic against the slugs a resource is recorded as
covering. Those slugs went straight to the page. On the DP mindset topic the
learner read:

```
FOCUS: dsa-dp-mindset-dp-mindset
FOCUS: dsa-dp-mindset-recognize-overlapping-subproblems-and-op
```

Machine text, truncated mid-word. The registry already carries a human
sentence per concept; the payload now uses it, and drops the redundant
`Understand <Topic>: <objective>` wrapper when the bare objective is also
present. Same topic, after:

```
FOCUS: Recognize overlapping subproblems and optimal substructure.
```

Coverage arithmetic still uses slugs and is untouched.

Separately, 57 topics had no concept contract at all, so their Focus panel was
empty — and each of them carried two or three authored `mastery_criteria` that
were exactly the right content for it:

```
FOCUS: Point at the exact line in a script that leaks when a scaler is fit
       on the full dataset before splitting.
FOCUS: State the rule that prevents preprocessing leakage in one sentence,
       and name the scikit-learn construct that enforces it.
```

Those were promoted into concepts, with one filter: a criterion reading
"Explain X in your own words" is not guidance, it is the filler shape, and
promoting it would put the emptiness back. Ten topics whose criteria were all
boilerplate got hand-written Focus lists instead. Two more recorded their
concepts as *optional* so coverage would not gate on them, which is a
readiness decision and not a reason to render nothing — the payload now falls
back to those.

**506 of 506 topics now show a Focus list**, and none of it claims a
verification nobody performed: `verification_status` was not touched.

### "Exact section" was often not a section

The same panel renders a resource's `section` as **"Exact section: ..."**, which
is a promise: this page is long, here is the part that is yours. The promise was
frequently empty.

104 primary resources stored a string derived from the URL itself —
`section: Git-Basics-Recording-Changes-to-the-Repository` under
`.../Git-Basics-Recording-Changes-to-the-Repository`, `section: 0` under
`cs50.harvard.edu/x/weeks/0/`. Another 132 stored nothing at all. Worse than
useless in the first case: it reads as though somebody pinned a section when
nobody did.

The honest answer turns out to depend on one thing — whether any other topic
opens the same page:

- **One topic owns the page.** Each Git Book page is one chapter on one
  subject. `FULL_SINGLE_PAGE`: read it, all of it.
- **Several topics share it.** Ten open the Missing Semester shell lecture,
  seven open CS50 Week 0. A boundary is genuinely needed and genuinely absent,
  so the misleading string is cleared and the resource marked `MULTI_TOPIC`,
  which makes the page warn instead of showing nothing. Admitting a gap only
  helps if the gap is visible.
- **The title already said it.** 101 DSA topics share Abdul Bari's algorithms
  playlist, and each row's title named its own video — "watch: Merge Sort". The
  instruction was sitting in the title while the section stayed empty, so the
  page warned that no boundary existed next to a title that answered it. Those
  were moved into `section`.

Every primary resource now answers the question, and none answers it silently:

| How much of this page is mine? | Rows |
| --- | --- |
| A named section or timestamp range | 282 |
| The whole page | 262 |
| No boundary — and the page says so | 78 |
| No boundary, no warning | **0** |

## 4. Questions

The third reason, documented in full at
[`backend/content/questions/README.md`](../backend/content/questions/README.md).

- **94 questions** were template filler: `Core idea of {TOPIC}?` with the
  distractors `A vague buzzword`, `Irrelevant outside interviews`,
  `Replaces prerequisites`. The answer is whichever option is a real sentence.
- **11 generic DP questions were attached to all 12 DP topics**, so the
  Knapsack page asked "Memoization vs tabulation:". This is the "not related"
  complaint stated exactly.
- **133 topics had no questions at all**, all of them in the AI and ML
  modules: `mod-dl-core` 32, `mod-ml-core` 27, `mod-cv` 26, `mod-nlp-core` 16,
  `mod-genai` 13, `mod-mlops` 10, `mod-math-jit` 9.

Questions are now authored per module under `backend/content/questions/`, and
the import gates make both defects hard errors — including a global check that
**no prompt may appear on two topics**, which is the DP defect expressed as a
rule.

25 banks were written, covering **239 topics with 1,121 authored questions**.
The remaining 210 topics — Domain 0, Java and most of DSA — already had
hand-written questions that were sound and were left alone, so the database now
holds **2,242 questions across all 449 topics**. Ten
questions predating the banks had prompts that said nothing on their own
(`Stable?`, `Common bug?`) and so collided across sibling topics; those were
rewritten in place by `repair_question_prompts.py`, which keeps their
neighbours untouched and validates each replacement through the same gates.

`python -m app.content.content_health` reports the state:

| Check | Before | After |
| --- | --- | --- |
| Topics with no questions | 133 | **0** |
| Topics with fewer than 4 questions | 227 | **0** |
| Template-filler questions | 94 | **0** |
| Prompts used on more than one topic | 22 | **0** |
| Topics with no PRIMARY resource | 0 | 0 |

One check does not read zero and should not: **42 PRIMARY resources still
serve more than one topic.** That is not automatically wrong — a long page
legitimately serves several topics when each is pinned to its own section —
but it is the condition under which questions drift toward being about the page
rather than about the topic, so the report lists them for review rather than
hiding them.

## 5. "NEEDS_REVIEW" told the learner to skip 188 topics

The topic page showed this whenever readiness was `NEEDS_REVIEW`:

> Resource exists but content verification is not trusted yet. **Prefer READY
> topics for daily study.**

188 of 449 topics are `NEEDS_REVIEW`, including **every one of the 26 computer
vision topics and all 32 deep-learning topics**. So the app was telling its
only user to avoid the entire AI curriculum — which is very likely why looking
for computer vision material felt like starting from nothing despite 26 mapped
CV topics sitting there.

The message conflated two separate facts. It now states both:

> The link below was fetched and confirmed to open the page it names on
> 2026-09-08. What has not been done is a read-through confirming it covers
> every concept listed under Focus. Study it as normal. If a Focus concept
> turns out to be missing from the page, that is worth recording rather than
> working around.

The readiness chip changed from "Needs review — not learner-verified" to
"Link checked · content review pending". No status field was altered to
achieve this: claiming `VERIFIED_COVERAGE` without doing the read-through
would be the same overstatement in the other direction.

## 6. A repair that only touches the database does not survive

This was learned the hard way, and it is the most transferable thing in this
document.

After the repairs above were applied, importing the curriculum index —
an ordinary, correct thing to do — silently undid a large part of the work:

| Reverted | Rows |
| --- | --- |
| Resource URLs | 16 |
| Section boundaries | 142 |
| **Template-filler questions restored** | **94** |

Nothing malfunctioned. Manifests under `content/curriculum/` are the source of
truth for the topics they define, `import_curriculum` upserts them, and the
manifests still held every original value — including `Core idea of {TOPIC}?`
with "A vague buzzword" as a distractor.

The underlying fault was **two files claiming the same field.** 106 topics had
questions defined in both a manifest and an authored bank, so whichever import
ran last won.

Two changes fixed it:

**Ownership is now explicit.** A topic with a bank in `content/questions/` has
its `questions:` block removed from the manifest. Questions live in exactly one
place. Manifest questions survive only for the 211 topics that have no bank —
the hand-written Domain 0, Java and DSA ones.

**Repairs are pushed back to source.** `sync_manifests` copies the repaired
`url`, `title`, `provider`, `role` and `section` from the database into the
matching manifest entry, and syncs question text for manifest-owned questions.
Deliberately narrow: exactly the fields the repair tooling writes, and nothing
else in a manifest is touched.

The round trip is now verified: `content_health` before and after a full index
re-import is byte-identical.

Related, and still open: **133 topics exist in no manifest at all.** Deep
Learning Core, Computer Vision, NLP Core, GenAI, MLOps and the just-in-time
maths were inserted by `content/d2_populate.py`. They are in the database and
in the committed snapshot, but not in reviewable YAML. That is why 49
prerequisite edges from the new modules had to move out of the manifests into
`apply_gap_prerequisites.py` — an edge pointing at a topic no manifest defines
can never resolve when the index is imported into an empty database, which is
what two of the tests do. That workaround is documented at the top of the file
it lives in, and the real fix is to express those 133 topics as manifests.

## 7. The curriculum grew by 57 topics

Ten subjects the owner named were missing entirely or nearly so. Each new topic
carries a verified PRIMARY resource, and most a REFERENCE too — 95 resources,
108 of 117 candidate URLs verified 200 with no redirect during research.

| Module | Topics | Covers |
| --- | --- | --- |
| `mod-py-tooling` | 6 | venv, `uv`, `pyproject.toml`, dependency pinning, lockfiles, interpreter versions |
| `mod-rl` | 6 | MDPs, policy vs value, Q-learning, policy gradients, RLHF mechanics, bandits for ranking |
| `mod-cloud` | 6 | service models, object storage, GPU instances and sizing, spot, managed inference, cost |
| `mod-ai-security` | 6 | OWASP LLM Top 10, prompt injection, exfiltration via tools, output handling, supply chain, PII |
| `mod-inference-perf` | 6 | quantization, KV cache, batching, memory-bound decoding, serving throughput |
| `mod-retrieval-quality` | 6 | reranking, hybrid search, chunking evaluation, ANN index choice |
| `mod-ml-data-quality` | 5 | **data leakage**, imputation, outliers, class imbalance, inconsistent preprocessing |
| `mod-ml-boosting` | 5 | boosted-tree theory, XGBoost tuning, categorical features, tabular vs deep learning |
| `mod-ml-timeseries` | 6 | why random splits fail, rolling-origin validation, baselines, accuracy metrics, lag features |
| `mod-mlops-cicd` | 5 | testing ML systems, continuous delivery for ML, production readiness |

Four honest gaps were recorded rather than papered over, and they are carried
in the topic descriptions so they are not silently lost:

- **Vector store selection** — no vendor-neutral comparison of FAISS, Chroma,
  pgvector and managed services exists; every candidate is marketing by one of
  them. The topic is anchored on FAISS's own index guidelines plus
  ANN-Benchmarks, which is measured data. A literal comparison lesson would
  have to be written, not linked.
- **Cloud cost** — GPU prices move monthly and no authoritative neutral page
  exists, so the topic teaches mechanisms (spot versus on-demand,
  right-sizing) and contains no numbers.
- **PII handling** — Microsoft Presidio's docs are orphaned and were
  deliberately not linked. This is the weakest pairing in an otherwise strong
  module.
- **CPU versus GPU inference** — no official page explains it as such; the
  honest framing is memory-bandwidth-bound decoding, and the best source is a
  personal blog that at least shows the arithmetic.

One caveat worth knowing: `uv` also appears as a SUPPLEMENT on three existing
topics (`cf-dependency-management`, `cf-dev-package-manager`, `py-syntax`),
because those teach `venv` and `pip` and a learner who has only seen those does
not know what a resolver or a lockfile buys them.

## 8. Running it

Start here. One command says whether the content is in good shape, and every
check that should read zero does:

```
cd backend
python -m app.content.content_health
#   -> reports/content_health.{json,md}
```

The rest, roughly in the order you would reach for them:

```
# fetch every mapped URL and classify what came back
python -m app.content.audit_resource_links
python -m app.content.audit_resource_links --record   # also stamp last_verified_at
#   -> reports/resource_link_audit.{json,md}

# apply the verified repairs (each target is re-fetched before it is written)
python -m app.content.repair_resource_links --dry-run
python -m app.content.repair_resource_links

# add a second source to a topic whose page is correct but incomplete
python -m app.content.add_resources --dry-run
python -m app.content.add_resources

# per-module authoring brief: topics, objectives, exact resource URLs
python -m app.content.question_briefs mod-cv
#   -> reports/question_briefs/mod-cv.md

# validate and load question banks
python -m app.content.import_questions --dry-run
python -m app.content.import_questions

# rewrite a specific legacy question whose prompt says nothing on its own,
# without touching the good questions beside it
python -m app.content.repair_question_prompts --dry-run
python -m app.content.repair_question_prompts

# push every repair back into the manifests, or the next curriculum import
# quietly undoes them
python -m app.content.sync_manifests --dry-run
python -m app.content.sync_manifests

# after importing the curriculum index, restore the prerequisite edges that
# point into the script-created topics no manifest defines
python -m app.content.apply_gap_prerequisites
```

Everything with a `--dry-run` writes a report to `reports/` either way, so you
can review a change before it lands and audit it afterwards.

**Order matters.** End a repair session with `sync_manifests`. Follow a
curriculum import with `import_questions` and `apply_gap_prerequisites`. The
check that you got it right is that `content_health` reads exactly the same
before and after a full index re-import — see section 6 for why.

The audit takes about 45 seconds over ~760 URLs at 16 workers. It is worth
re-running periodically: publishers reorganise, and this audit found that
GeeksforGeeks had moved its entire operating-systems and DSA sections behind
new path prefixes since the links were recorded.

## 9. What this changes about trusting the database

The lesson is narrow and worth keeping. Every check in this repository before
today validated the database against itself, and all of them passed while 57
links served source text and nine pointed at a course edition that does not
exist. Internal consistency is not correctness when the content lives on
someone else's server.

`tests/test_content_integrity.py` locks in the classifier behaviour and the
raw-to-rendered mappings offline, so the fixes cannot silently regress, and
validates every committed question bank on every test run.
