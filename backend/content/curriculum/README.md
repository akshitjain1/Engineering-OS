# Curriculum content

| Kind | Location | Purpose |
| --- | --- | --- |
| **DEMO** | `demo/` | Small fixture used by `seed.py` and local UI testing |
| **OFFICIAL V1** | `foundation/`, `programming/`, `dsa/`, `v1-index.yaml` | Domains 0–2 authored content |
| **Later domains** | other folders | Placeholders only |

Import:

```
cd backend
python -m app.content.import_curriculum content/curriculum/demo/rest-apis.yaml
python -m app.content.import_curriculum content/curriculum/v1-index.yaml
```

Regenerate official YAML (structure emitter skips authored domains):

```
python content/emit_v1.py
python content/d0_populate.py
python content/d1_populate.py
python content/d2_populate.py
```

Do not put the real curriculum in `demo/`.
Do not invent resource URLs in these manifests.
Do not hard-code curriculum inside FastAPI routes or React pages.
