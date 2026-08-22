# Domain 2 resource mappings

Authoring: `backend/content/d2_populate.py`. `emit_v1.py` does not overwrite Domain 2. Domains 0–1 are frozen.

## PRIMARY (Abdul Bari)

- Channel: `https://www.youtube.com/@Abdul_bari`
- Algorithms playlist (used when a specific video ID was not oEmbed-verified): `https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O`
- Verified videos (oEmbed author_name = Abdul Bari):
  - Introduction to Algorithms: `https://www.youtube.com/watch?v=0IAPZzGSbME`
  - QuickSort: `https://www.youtube.com/watch?v=7h1s2SojIRw`
  - Heap / HeapSort / Heapify / PQ: `https://www.youtube.com/watch?v=HqPJF2L5h9U`
  - 0/1 Knapsack DP: `https://www.youtube.com/watch?v=nLmhmB6NzcM`

Exact video IDs for other lectures remain **unresolved**; titles in PRIMARY resources name the intended lecture.

## PRACTICE

- NeetCode Core Skills: `https://neetcode.io/practice/practice/coreSkills`
- NeetCode 150: `https://neetcode.io/practice/practice/neetcode150`
- LeetCode: **unmapped**. Study-plan and `/problems/` pages returned Cloudflare 403 from this environment. NeetCode 150 is the verified interview-practice collection.

## DEEP DIVE

MIT OCW 6.006 Spring 2020 lecture pages (verified HEAD 200), used selectively — not a mandatory full course.

## C++

Equivalence lives in topic descriptions (no C++ resource URLs). Java `PriorityQueue` min-heap vs C++ `priority_queue` max-heap is explicit on heap topics.
