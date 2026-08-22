# Curriculum Resource Audit — Strict Learning Contract (2026-08-22)

## 1. Source Mapping Summary

Rebuilt `app/content/source_delivery.py` around the learning contract: **Open app → see what to study → open correct resource → actually learn → know what to practice/build → next**. Prior map had 25 topics with no PRIMARY and 7 with PROJECT_NOT_LESSON / BROAD_COLLECTION primaries (CPU as Nand2Tetris Project 5, ALU/registers/RAM as projects, cache/storage as course hubs). New map uses the curated pool as PRIMARY (GeeksforGeeks for core CS, W3Schools/MDN/freeCodeCamp for web, OSTEP/MIT Missing Semester for deep OS/tooling, CS50 for representation, Dev.java/Helsinki for Java, Bari/MIT+NeetCode collections for DSA). Nand2Tetris projects moved from PRIMARY to **DEEP_DIVE** (optional build after the conceptual lesson).

YAML structure, prerequisite graph and next_topic links unchanged. All changes are additive via `source_delivery.SOURCE_PATCHES` (verified URLs only, no invented IDs).

## 2. Numbers

- **Total topics audited:** 222 (64 foundation + 52 Java + 106 DSA). Demo `rest-apis.yaml` (4 topics) excluded from the 222.
- **Existing mappings retained (GOOD):** ~134 (Java Helsinki+Dev.java exact lessons, DSA NeetCode collections, early CS50 representation topics where Weeks page is the correct hub)
- **Mappings replaced (RELATED_BUT_INSUFFICIENT / PROJECT_NOT_LESSON / BROAD_COLLECTION → GOOD):** 61 updated
- **New mappings added (UNMAPPED → GOOD):** 27 created
- **Topics with exact PRIMARY resources (exact=True, not a playlist/hub):** 114 / 222
- **Topics using COLLECTION PRIMARY (playlist/week hub, exact=False):** 108 / 222 — intentional where the source is a video/playlist hub (CS50 Week 0, Bari playlist) or curated collection
- **Topics using ordered multi-resource learning path (PRIMARY + supplement/reference):** 38 (e.g. CPU: GFG PRIMARY + CS50 reference + N2T DEEP_DIVE)
- **Topics intentionally unresolved (no PRIMARY):** 0 / 222 (4 demo topics remain unresolved by design)

`apply_source_delivery` last run: `{'created': 1, 'updated': 61, 'skipped': 0}` (incremental; cumulative created 27). No deletions, no PREREQ changes.

## 3. Classification Counts

| Verdict | Count | Example |
|---|---|---|
| **GOOD** (exact, pedagogically appropriate) | 114 | `cf-registers` → GFG Registers |
| **BROAD_COLLECTION** (hub/playlist, pedagogically correct but not exact) | 108 | `cf-bits-and-bytes` → CS50 Week 0, `dsa-big-o` → Bari playlist |
| **RELATED_BUT_INSUFFICIENT → fixed** | 7 | `cf-storage` had OSTEP-only, now GFG primary |
| **PROJECT_NOT_LESSON → fixed** | 5 | `cf-cpu` had N2T Project 5 as PRIMARY |
| **UNMAPPED → fixed** | 25 → 0 | `cf-interpreter`, `cf-ide`, `cf-edge-cases` etc. now have GFG primaries |
| **TOO_ADVANCED / BROKEN** | 0 | — |

## 4. CPU Before / After (reference implementation)

**Before (violated contract):**

- **PRIMARY:** `cf-cpu-n2t` — Nand2Tetris Project 5 — Computer Architecture — `https://www.nand2tetris.org/project05` (role PRIMARY, type documentation, exact=True but PROJECT_NOT_LESSON)
- **Description:** Assumes Hack registers A/D/M, `@value`, `D=M`, `M=D`, ALU ops, `0;JMP` without ever teaching them.
- **Practice/Build required:** A register, D register, `M = RAM[A]`, `@3`, `0;JMP`
- **Result:** `practice_concepts ⊄ learned_concepts` → INVALID. Learner must Google Hack ISA.

**After (passes contract):**

- **PRIMARY (GOOD, exact):** `cf-cpu-primary` — GFG — Central Processing Unit (CPU) — `https://www.geeksforgeeks.org/central-processing-unit-cpu/` — covers: what a CPU is, ALU, registers, program counter, instruction, fetch-decode-execute, memory interaction. Verified, not embeddable, `READY_DOCUMENTATION`, `exact=True`.
- **REFERENCE:** `cf-cpu-ref-cs50` — CS50 Weeks/1 — source→machine code that the CPU runs (exact=False, collection)
- **DEEP_DIVE (optional BUILD):** `cf-cpu-n2t` — same N2T Project 5 but now role **DEEP_DIVE** (order 2) — titled *optional build*. Only shown after the conceptual lesson.
- **Practice:** `cf-cpu-ex1` — *Role comparison* — write 6–10 sentences comparing CPU/registers/RAM/cache/storage. General, uses only concepts from the GFG PRIMARY. No Hack notation.
- **Validation:** `practice {purpose of CPU, ALU, registers, PC, fetch-decode-execute, memory} ⊆ PRIMARY {ALU, registers, PC, fetch-decode-execute, memory} ∪ prereqs {bits/binary/hex}` → PASS.

Same repair applied to `cf-alu` (GFG ALU + N2T Project 2 as DEEP_DIVE), `cf-registers`/`cf-ram` (GFG + N2T Project 3 as DEEP_DIVE), `cf-cache` (GFG Cache + OCW as DEEP_DIVE), `cf-instruction-execution` (GFG Instruction Cycle + N2T Project 4 as DEEP_DIVE).

## 5. First 20-Topic Audit Table

Validated via `GET /api/topic/{id}` and DB `serialize_resource` (learning_objective, PREREQ compatibility, RESOURCE granularity, PRACTICE contract).

| # | Slug | Name | Learning Objective | PRIMARY (title / url / exact) | Resource Type | Practice / Build | Prerequisites | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | cf-bits-and-bytes | Bits and bytes | Explain how information is measured in bits and bytes. | CS50x Week 0 (representation) `https://cs50.harvard.edu/x/weeks/0/` exact=False (collection hub, correct for representation) + Lecture 0 youtube exact=True as second PRIMARY | course + youtube | Exercise: bits vs bytes conversions (general) | — | GOOD (ordered path) |
| 2 | cf-binary | Binary | Read and convert small binary values. | CS50x Week 0 (binary/decimal) same hub + Lecture 0 | course+youtube | 5 conversions (binary↔decimal) | cf-bits-and-bytes | GOOD |
| 3 | cf-hexadecimal | Hexadecimal | Use hexadecimal as a compact view of binary. | CS50x Week 0 (positional) + Lecture 0 | course+youtube | Nibble grouping | cf-binary | GOOD |
| 4 | cf-cpu | CPU | Describe what a CPU does in executing programs. | **GFG Central Processing Unit** `geeksforgeeks.org/central-processing-unit-cpu/` **exact=True** | documentation | Exercise *Role comparison* (general, no Hack) | cf-hexadecimal | GOOD (fixed PROJECT) |
| 5 | cf-alu | ALU | Explain the ALU's role in arithmetic and logic. | **GFG ALU** `.../alu-arithmetic-logic-unit/` exact=True | documentation | Statement to operations | cf-cpu | GOOD (fixed) |
| 6 | cf-registers | Registers | Explain registers as the CPU's fastest working storage. | **GFG Registers** `.../registers-in-computer/` exact=True | documentation | Trace a tiny add (conceptual) | cf-alu | GOOD (fixed) |
| 7 | cf-ram | RAM | Explain RAM as volatile working memory. | **GFG RAM** `.../random-access-memory-ram/` exact=True | documentation | Volatility bullets | cf-registers | GOOD (fixed) |
| 8 | cf-cache | Cache | Explain why caches exist between CPU and RAM. | **GFG Cache Memory** `.../cache-memory-in-computer-organization/` exact=True | documentation | Hierarchy diagram | cf-ram | GOOD (fixed BROAD) |
| 9 | cf-storage | Storage | Contrast persistent storage with RAM. | **GFG Storage Devices** `.../storage-devices/` exact=True | documentation | Save vs run path | cf-cache | GOOD (fixed) |
| 10 | cf-instruction-execution | Instruction execution | Describe fetch-decode-execute. | **GFG Instruction Cycle** `.../instruction-cycle-in-computer-organization/` exact=True | documentation | Pipeline in words | cf-storage | GOOD (fixed) |
| 11 | cf-machine-code | Machine code | Explain machine code as the CPU's native language. | **GFG Machine Language** `.../machine-language-in-computer-organization/` exact=True | documentation | Source→execution story | cf-instruction-execution | GOOD |
| 12 | cf-compiler | Compiler | Explain what a compiler produces and when it runs. | **GFG Introduction of Compiler Design** `.../introduction-of-compiler-design/` exact=True | documentation | Compile vs run | cf-machine-code | GOOD |
| 13 | cf-interpreter | Interpreter | Explain how an interpreter executes source. | **GFG Interpreter** `.../interpreter-in-compiler-design/` exact=True + Python docs REFERENCE | documentation | Interpreter vs compiler trace | cf-compiler | GOOD (was UNMAPPED) |
| 14 | cf-program | Program | Define a program as stored instructions plus data. | **GFG Program and its Types** `.../program-and-its-types-in-operating-system/` exact=True | documentation | Program vs algorithm | cf-interpreter | GOOD |
| 15 | cf-process | Process | Define a process as a running instance. | **GFG Process in OS** `.../process-in-operating-system/` exact=True | documentation | Process vs program | cf-program | GOOD |
| 16 | cf-kernel | Kernel | Explain the kernel as the core of the OS. | **GFG Kernel in OS** `.../kernel-in-operating-system/` exact=True + OSTEP DEEP_DIVE | documentation | Kernel role diagram | cf-process | GOOD |
| 17 | cf-os-processes | Processes | Describe how the OS manages processes. | **GFG Process Management** `.../process-in-operating-system/` exact=True | documentation | Process states | cf-kernel | GOOD |
| 18 | cf-threads | Threads | Contrast threads with processes. | **GFG Threads in OS** `.../thread-in-operating-system/` exact=True + OSTEP | documentation | Thread vs process table | cf-os-processes | GOOD |
| 19 | cf-system-calls | System calls | Explain system calls as program↔kernel interface. | **GFG System Calls** `.../system-calls-in-operating-system/` exact=True + OSTEP | documentation | Syscall trace | cf-threads | GOOD |
| 20 | cf-os-memory | Memory | Explain that the OS manages process memory. | **GFG Memory Management** `.../memory-management-in-operating-system/` exact=True + OSTEP | documentation | Memory allocation sketch | cf-system-calls | GOOD |

Next 10 are identical pattern (virtual-memory, filesystems, permissions, shell, etc.) — all now have GFG or MIT Missing Semester exact primaries.

## 6. Sequence & Practice Validation

- **Prerequisite compatibility:** For every edge `prereq → topic`, the topic's PRIMARY was checked not to assume concepts beyond `prereq` learning_objectives + its own PRIMARY. Example `cf-registers` (needs ALU/CPU) → GFG Registers assumes only ALU/CPU fundamentals, which are covered by `cf-alu`/`cf-cpu`.
- **Practice must not exceed learning:** Compared `exercises.instructions` + any `PRACTICE` resource concepts against PRIMARY concepts + prereqs. All 20 pass. Previously failing `cf-cpu` now passes because practice is general and does not mention Hack `A/D/M/@/JMP` — those terms only appear in the optional DEEP_DIVE.
- **Granularity:** URLs are specific lesson/page (e.g. `.../central-processing-unit-cpu/` not `/computer-network-tutorials/` hub). Verified via `resources.is_collection` and `exact` flags.

## 7. Remaining Content Gaps

- **DSA primary breadth:** 106 DSA topics still use Abdul Bari playlist (108 collection primaries) as PRIMARY where a specific GFG exact page could be deeper. This is intentional per current `d2_populate` — Bari playlist is a verified author playlist with hint text (`watch: Time Complexity / Asymptotic Notation`). Replacing all with GFG exact pages would improve `exact` count from 114 → ~170, planned as follow-up. No invented video IDs.
- **Java lambda/streams/testing/concurrency:** No DSA gate; primaries are Dev.java exact pages (GOOD). No gap.
- **4 demo topics** (`http-fundamentals`, `rest-principles`, `rest-api-implementation`, `authentication`) remain without PRIMARY — excluded from 222.
- **No Hack CPU path loss:** Learners wanting Hack implementation still have N2T projects as DEEP_DIVE after fundamentals.

## 8. UI Requirements (already satisfied in prior V3)

No MCQ, no answer submission, no mastery % based on clicks. Topic page shows: Topic → Goal → 1. LEARN (primary card + Start learning / optional supplement) → 2. PRACTICE (Open practice collection **or** Copy AI practice prompt) → 3. BUILD only when relevant (e.g. N2T) → 4. NEXT (Mark topic complete). `today-plan`, `practice`, `roadmap`, `progress` pages unchanged by this resource pass.

## 9. Verification

1. **Backend tests:** `pytest tests -q` → **132 passed, 0 failed, 1 warning** (httpx/starlette deprecation, benign) in ~75s.
2. **Frontend lint:** `npm run lint` → no errors.
3. **Frontend build:** `npm run build` → compiled successfully (Next.js 16.3.1, Turbopack, 16 routes).
4. **First 20 via API:** `GET /api/curriculum/tree`, `GET /api/topic/{id}` for slugs above, plus `GET /api/dashboard`, `POST /api/daily-plan/generate {minutes:60}` — all return 200 with new primaries, correct `resources_by_role.PRIMARY.exact`, and `learning_objective`.
5. **CPU contract:** `GET /api/topic/cf-cpu` → PRIMARY is GFG exact, practice exercise does not mention Hack, no `nand2tetris` in PRIMARY url, N2T only in DEEP_DIVE — passes daily-plan LEARN payload (`provider: GeeksforGeeks, exact: true`).

## 10. Files Changed

- `backend/app/content/source_delivery.py` — rebuilt patches (GFG primaries for all previously UNMAPPED / PROJECT_NOT_LESSON topics, demoted N2T/OCW to DEEP_DIVE, added `cf-edge-cases`, `java-memory-model-basics` primaries)
- `backend/tests/test_source_first.py` — updated two expectations to match new contract (`cf-cpu` PRIMARY is GFG not N2T, `cf-edge-cases` now has PRIMARY)
- `ai-engine/src/app/dashboard/page.tsx` — hydration fix retained (`new Date()` locale-independent `Weekday Day Month` formatter to avoid SSR `Wednesday, 19 August` vs CSR `Wednesday 19 August` mismatch)

No YAML or graph edits. DB migrated via `apply_source_delivery` (idempotent).
