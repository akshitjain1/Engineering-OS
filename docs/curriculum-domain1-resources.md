# Domain 1 resource mappings

Authoring script: `backend/content/d1_populate.py`. Do not overwrite Domain 1 with `emit_v1.py`. Domain 0 is frozen.

## Layers

- **PRIMARY / PRACTICE:** University of Helsinki Java Programming I/II (`https://java-programming.mooc.fi/`) — exercise-heavy, **legacy/unmaintained**. Not authoritative for modern Java or required NetBeans/TMC tooling.
- **REFERENCE:** [Dev.java Learn](https://dev.java/learn/) — modern language and API.
- **Exceptions:** JUnit 5 user guide (testing); Oracle Java Tutorial concurrency trail (threads/sync — Dev.java has no basic Thread chapter); Oracle JDK 21 API pages for PriorityQueue and Comparable.

## Helsinki coverage (verified part/section URLs)

Mapped where the section actually exists: Parts 1–6, 8–12, 14 (selected sections). Part 7 (algorithms/larger exercises) is not a Java-language module here. Part 13 GUI is unused. HashSet has no dedicated Helsinki section — Dev.java Set is PRIMARY; Part 8 HashMap is PRACTICE only.

## Unmapped PRIMARY

- `java-memory-model-basics` — internal stack/heap lesson; Dev.java GC overview as REFERENCE only.

## DSA gates (unchanged graph)

Methods, arrays, strings, classes, references, List/Set/Map, PriorityQueue, Comparable/Comparator. Streams, lambdas, concurrency, JVM, packages are **not** DSA prerequisites.
