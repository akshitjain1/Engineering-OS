# Curriculum manifest

Curriculum content is **data**, not application code.

- **DEMO** content: `backend/content/curriculum/demo/` — small fixture for development (`seed.py`).
- **OFFICIAL V1 structure**: Domains 0–2 under `foundation/`, `programming/`, and `dsa/`, listed in `v1-index.yaml`.
- Later domains remain empty placeholders.

Do not hard-code tracks, topics, or lessons in FastAPI routes or React components.

Official V1 is **structure only** in this phase: topics, prerequisites, objectives, mastery criteria, and resource *slots* without URLs. Questions and exercises are empty until the mapping phase. Regenerating YAML: `python content/emit_v1.py` from `backend/`. Java and DSA are not a single forced sequence: DSA units require only the minimum Java needed to implement that unit.

## Format

YAML or JSON. `schema_version: 1`.

```yaml
schema_version: 1
kind: curriculum_manifest
origin: demo | official
track:
  slug: software-engineering
  name: Software Engineering
  description: ...
  order: 0
  levels:
    - slug: fundamentals
      name: Level 1: Fundamentals
      subjects:
        - slug: backend-development
          name: Backend Development
          modules:
            - slug: rest-apis
              name: REST APIs
              topics:
                - slug: http-fundamentals
                  name: HTTP Fundamentals
                  prerequisites: []          # topic slugs, not display names
                  lessons:
                    - slug: http-methods
                      title: HTTP Methods
                      description: ...
                      order: 0
                      hours_estimated: 1.5
                      resources:
                        - slug: mdn-http
                          title: MDN HTTP Overview
                          type: documentation
                          url: https://developer.mozilla.org/...
                          provider: MDN
                          official: true
                          order: 0
                      questions:
                        - slug: safe-method
                          prompt: Which HTTP method is idempotent and safe?
                          options: [GET, POST, PATCH, CONNECT]
                          answer: GET
                          explanation: ...
                      exercises:
                        - slug: status-codes
                          title: List common HTTP status codes
                          instructions: ...
                          difficulty: beginner
```

`slug` values must be unique across the whole file (`kebab-case`). Integer primary keys remain internal to the database.

## Supported fields

| Entity | Required | Notes |
| --- | --- | --- |
| track / level / subject / module / topic | `slug`, `name` | `order`, `description` optional |
| topic | `prerequisites` | list of **topic slugs** |
| topic | `learning_objective`, `mastery_criteria`, `next_topic` | stored on import into the topic description |
| lesson | `slug`, `title`, `order` | unique `order` per topic |
| resource | `slug`, `title`, `type` | `url` optional until mapped; `provider` and `role` optional |
| resource `role` | | `PRIMARY`, `REFERENCE`, `PRACTICE`, `DEEP_DIVE` |
| question | `slug`, `prompt`, `options`, `answer` | `answer` must be one of `options` |
| exercise | `slug`, `title`, `instructions` | stored as lesson exercise description |

Resource `type`: `youtube_video`, `youtube_playlist`, `documentation`, `article`, `book`, `interactive_tutorial`, `github_repo`, `exercise`, `coding_problem`, `other`.

Optional `topic` / `module` / `subject` slug fields on nested children must match their actual parent.

## Import command

From `backend/`:

```
python -m app.content.import_curriculum content/curriculum/demo/rest-apis.yaml
python -m app.content.import_curriculum content/curriculum/v1-index.yaml
```

`v1-index.yaml` imports Domains 0, 1, then 2 in order so cross-domain prerequisites resolve.

Prefer the index for official V1. `--dir content/curriculum` also picks up the **demo** fixture; it skips `_examples/` and `v1-index.yaml`.

`python seed.py` imports the **demo** manifest only, then ensures DSA patterns and the `akshit` user row. It does not load official V1.

## Validation

The importer validates **before writing**. Any error rolls back the transaction.

- duplicate slugs
- missing prerequisite slugs (unless that topic already exists in the DB)
- missing `next_topic` slugs (must be a topic in the same file, already in the DB, or in the same import group)
- circular prerequisites
- invalid parent / lesson references
- invalid resource URLs (scheme + host only; no network fetch). Resources with **no URL** are valid and are skipped at import (`skipped_resources`)
- duplicate lesson order within a topic
- missing required fields / answer not in options

## Update behavior

Re-importing the same file:

- creates rows that do not exist (match by `slug`, then by name/title within the parent)
- updates content fields (name, description, URL, options, …)
- **does not** reset lesson/resource/exercise completion, question attempts, or `user_progress`
- **does not** delete topics/lessons that were removed from the file

## Demo vs real

| | Demo | Official V1 |
| --- | --- | --- |
| `origin` | `demo` | `official` |
| Size | one REST module | Domains 0–2 structure (URLs/exercises still unmapped) |
| Loader | `seed.py` | `v1-index.yaml` |

The curriculum explorer can display either. Do not mix official content into `demo/`.

Curriculum V1 is **not complete**: resource URLs, conceptual questions, and exact problem sets are still unmapped.
