# Question banks

Self-check questions, one YAML file per curriculum module.

A question here is not a quiz for its own sake. The learner has just opened the
PRIMARY resource the app told them to open and read it. The question checks
whether they took the right thing from that page. That is the only job.

## Why this directory exists

Questions used to be generated, and they went wrong in two ways that a learner
noticed before any tooling did.

**Template filler.** 94 questions read `Core idea of {TOPIC}?`, with the options:

```
A vague buzzword
Explain layers, activations, and forward pass.
Irrelevant outside interviews
Replaces prerequisites
```

The answer is whichever option is a real sentence. You can score full marks
knowing nothing.

**Module questions on topic pages.** One set of eleven generic dynamic-
programming questions was attached to all twelve DP topics. The Knapsack page
asked "Memoization vs tabulation:". So did Grid DP, and Interval DP. Studying
one thing and being quizzed on its neighbour is exactly what makes content feel
unrelated to what you are learning.

Both are now import errors. See `app/content/question_bank.py`.

## Format

```yaml
schema_version: 1
kind: question_bank
module: mod-cv
topics:
  - topic: cv-color-spaces          # must be an existing curriculum topic slug
    questions:
      - id: cv-hsv-why              # unique slug; answer history is keyed to it
        prompt: Why is HSV usually a better colour space than RGB for thresholding by colour?
        options:
          - "Hue separates colour from brightness, so a threshold survives lighting change"
          - "HSV uses fewer bits per pixel, which makes the threshold faster to compute"
          - "HSV stores its colours as integers, whereas RGB stores them all as floats"
          - "HSV is linear in perceived brightness, so equal steps look equally bright"
        answer: "Hue separates colour from brightness, so a threshold survives lighting change"
        explanation: >-
          In RGB, shading a red object changes all three components together, so a fixed
          range fails. HSV isolates the colour into hue and pushes illumination into value.
          HSV is the same bit depth as RGB, and neither space is perceptually uniform.
        difficulty: intermediate     # beginner | intermediate | advanced
        mastery: true                # must be right to claim the topic
```

## The gates

Import refuses a bank that breaks any of these. Each one blocks a defect that
actually shipped:

| Gate | Blocks |
| --- | --- |
| No prompt repeated on another topic, in this file or the database | The DP set copied across twelve topics |
| Prompt is not a name-restating template | `Core idea of {TOPIC}?` |
| Banned phrasing rejected | `a vague buzzword`, `none of the above`, `TBD` |
| At least 4 options, distinct, none blank, answer matches one exactly | Unanswerable or ambiguous questions |
| Option lengths within 3x of each other | Answers guessable from shape without reading |
| Explanation at least 15 words | "Because it is axis 2." — which teaches nothing |
| At least 4 questions per topic | A single question standing in for a topic |
| Topic slug must exist in the curriculum | Questions attached to nothing |

The explanation gate is the one worth taking seriously. Say **why the wrong
options are wrong**. That sentence is where the learning happens, and it is
what you will reread six weeks later when the topic comes back for revision.

## Writing a bank

Generate a brief first. It gives you every topic in the module with its
objective and the exact resource URL the learner is sent to, so questions stay
anchored to what they actually read:

```
python -m app.content.question_briefs mod-cv
# -> reports/question_briefs/mod-cv.md
```

Then validate as you write. Iterate until it reports zero errors:

```
python -m app.content.import_questions content/questions/mod-cv.yaml --dry-run
```

And import:

```
python -m app.content.import_questions                    # every bank
python -m app.content.import_questions content/questions/mod-cv.yaml
```

Import is idempotent and replaces that topic's questions. Answer history
survives: a question keeps its attempt count and last result as long as its
`id` does not change, so fixing a typo in an explanation does not reset what
you have already answered.

## What a good question looks like

Prefer a situation over a definition. Compare:

> What is data leakage?

against

> You fit the scaler on the full dataset before splitting, and your validation
> score is suspiciously high. What happened?

The second tests whether you would catch it in your own code, which is the
thing an interviewer is actually probing and the thing that costs you a
production model. The first tests whether you remember a phrase.

Distractors should be misconceptions someone genuinely holds. If a distractor
is obviously silly it is doing no work, and it makes the question easier than
the topic.

## Tests

`tests/test_content_integrity.py` validates every bank in this directory
offline, on every test run, plus the exact filler question and the exact
cross-topic duplication that shipped. A bad bank fails the suite before it can
reach the database.

## What is here

| Bank | Topics | Questions |
| --- | --- | --- |
| `mod-ai-eng-shell` | 2 | 8 |
| `mod-ai-security` | 6 | 30 |
| `mod-be-http` | 7 | 35 |
| `mod-cloud` | 6 | 30 |
| `mod-cv` | 26 | 121 |
| `mod-db-sql` | 5 | 25 |
| `mod-devops-shell` | 2 | 8 |
| `mod-dl-core` | 32 | 160 |
| `mod-dl-shell` | 2 | 8 |
| `mod-dl` | 4 | 20 |
| `mod-ds-core` | 5 | 26 |
| `mod-dsa-dp` | 12 | 60 |
| `mod-genai-shell` | 2 | 8 |
| `mod-genai` | 17 | 83 |
| `mod-inference-perf` | 6 | 30 |
| `mod-math-jit` | 9 | 45 |
| `mod-math-ml` | 6 | 30 |
| `mod-ml-boosting` | 5 | 25 |
| `mod-ml-core` | 35 | 140 |
| `mod-ml-data-quality` | 5 | 25 |
| `mod-ml-timeseries` | 6 | 30 |
| `mod-mlops-cicd` | 5 | 25 |
| `mod-mlops` | 14 | 70 |
| `mod-net-core` | 6 | 27 |
| `mod-nlp-core` | 16 | 80 |
| `mod-nlp-shell` | 2 | 8 |
| `mod-ops-core` | 6 | 30 |
| `mod-py-core` | 5 | 25 |
| `mod-py-tooling` | 6 | 30 |
| `mod-retrieval-quality` | 6 | 30 |
| `mod-rl` | 6 | 30 |
| `mod-se-core` | 10 | 43 |
| `mod-sysdesign-shell` | 2 | 8 |
| `mod-sysdesign` | 4 | 20 |
| `mod-web-core` | 8 | 33 |
| **Total** | **296** | **1406** |

The other 210 topics — Domain 0, Java and most of DSA — already had
hand-written questions that were sound, and were left alone. Ten of those had
prompts that said nothing without the page around them (`Stable?`,
`Common bug?`, `Common mistake?`) and so collided across sibling topics; those
were rewritten in place by `app/content/repair_question_prompts.py`, which
updates the specific rows and leaves their neighbours untouched.

Across the database that is **2,527 questions over 506 topics**, with no topic
below four and no prompt appearing on two topics.

## One thing the authors kept finding

The 35 banks were written against each topic's mapped resource. That exercise
turned up roughly forty resource mappings that load a real page which is not
the topic — the class of defect no link checker can see, because the URL is
fine. Examples that were fixed as a result:

- `cv-u-net` pointed at d2l's Fully Convolutional Networks page. D2L has no
  U-Net page, and FCN fuses by addition with no symmetric decoder, so a U-Net
  question was unanswerable from it.
- `dl-loss-functions-nn` pointed at the MLP page, which never derives
  cross-entropy. That is in the softmax-regression chapter.
- `math-covariance-correlation` pointed at a statistics page whose only
  sections are estimator bias, hypothesis testing and confidence intervals.
- `ml-classification` and `ml-decision-trees` shared one StatQuest video, and
  `mlops-drift-quality` had a metric-suite page as its primary while the
  Google guide that actually teaches training/serving skew sat in the
  supplement slot.

Writing a question against a page is the cheapest content review there is: you
cannot write four honest questions from a page that does not cover the topic.
If you write a bank and find yourself reaching past the mapped resource, that
is a finding about the mapping, not a failure of yours — record it.
