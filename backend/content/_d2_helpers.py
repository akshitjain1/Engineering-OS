"""Verified URLs and helpers for Domain 2 DSA authoring. No invented video IDs or LeetCode slugs."""

from __future__ import annotations

# Abdul Bari — oEmbed author_name == "Abdul Bari" (verified this session).
BARI_CH = "https://www.youtube.com/@Abdul_bari"
BARI_PL = "https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O"
BARI_INTRO = "https://www.youtube.com/watch?v=0IAPZzGSbME"  # 1. Introduction to Algorithms
BARI_QUICK = "https://www.youtube.com/watch?v=7h1s2SojIRw"  # 2.8.1 QuickSort Algorithm
BARI_HEAP = "https://www.youtube.com/watch?v=HqPJF2L5h9U"  # 2.6.3 Heap / HeapSort / Heapify / PQ
BARI_KNAP = "https://www.youtube.com/watch?v=nLmhmB6NzcM"  # 4.5 0/1 Knapsack DP

NC_CORE = "https://neetcode.io/practice/practice/coreSkills"
NC_150 = "https://neetcode.io/practice/practice/neetcode150"

# User-specified LeetCode collection. Automated HEAD/GET returned Cloudflare 403 (not 404).
# Do not attach invented /problems/<slug>/ URLs.
LC_PLAN = "https://leetcode.com/studyplan/"

MIT = "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020"
MIT_HOME = MIT + "/"
MIT_VIDS = MIT + "/resources/lecture-videos/"
MIT_NOTES = MIT + "/resources/lecture-notes/"
MIT_L1 = MIT + "/resources/lecture-1-algorithms-and-computation/"
MIT_L2 = MIT + "/resources/lecture-2-data-structures-and-dynamic-arrays/"
MIT_L3 = MIT + "/resources/lecture-3-sets-and-sorting/"
MIT_L4 = MIT + "/resources/lecture-4-hashing/"
MIT_L5 = MIT + "/resources/lecture-5-linear-sorting/"
MIT_L6 = MIT + "/resources/lecture-6-binary-trees-part-1/"
MIT_L7 = MIT + "/resources/lecture-7-binary-trees-part-2-avl/"
MIT_L8 = MIT + "/resources/lecture-8-binary-heaps/"
MIT_L9 = MIT + "/resources/lecture-9-breadth-first-search/"
MIT_L10 = MIT + "/resources/lecture-10-depth-first-search/"
MIT_L11 = MIT + "/resources/lecture-11-weighted-shortest-paths/"
MIT_L12 = MIT + "/resources/lecture-12-bellman-ford/"
MIT_L13 = MIT + "/resources/lecture-13-dijkstra/"
MIT_L14 = MIT + "/resources/lecture-14-apsp-and-johnson/"
MIT_L15 = MIT + "/resources/lecture-15-dynamic-programming-part-1-srtbot-fib-dags-bowling/"
MIT_L16 = MIT + "/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/"
MIT_L17 = MIT + "/resources/lecture-17-dynamic-programming-part-3-apsp-parens-piano/"
MIT_L18 = MIT + "/resources/lecture-18-dynamic-programming-part-4-rods-subset-sum-pseudopolynomial/"
MIT_L19 = MIT + "/resources/lecture-19-complexity/"
MIT_L20 = MIT + "/resources/lecture-20-course-review/"

RELEARN = (
    "You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, "
    "not a first course in programming."
)
JAVA_PRIMARY = "Implement in Java. C++ is an equivalence note, not a second curriculum."
BARI_UNRESOLVED = (
    "Exact Abdul Bari video ID not verified this session. Use the official Algorithms playlist "
    "and watch the matching titled lecture. Do not use third-party reuploads."
)


def r(slug, title, url, provider, role, rtype, order, description):
    return {
        "slug": slug,
        "title": title,
        "type": rtype,
        "url": url,
        "provider": provider,
        "role": role,
        "description": description,
        "official": True,
        "order": order,
    }


def q(slug, prompt, options, answer, explanation, difficulty="medium", mastery=False):
    assert answer in options, slug
    assert len(options) == 4, slug
    return {
        "slug": slug,
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "difficulty": difficulty,
        "mastery_requirement": mastery,
    }


def ex(slug, title, instructions, difficulty="intermediate", order=0):
    return {
        "slug": slug,
        "title": title,
        "instructions": instructions,
        "difficulty": difficulty,
        "order": order,
    }


def unit(hours, explanation, mastery, resources, questions, exercises, objective=None):
    return {
        "hours_estimated": hours,
        "explanation": explanation,
        "mastery_criteria": mastery,
        "resources": resources,
        "questions": questions,
        "exercises": exercises,
        "learning_objective": objective,
    }


def bari_primary(slug, watch_hint):
    return r(
        f"{slug}-primary",
        f"Abdul Bari Algorithms playlist — watch: {watch_hint}",
        BARI_PL,
        "Abdul Bari",
        "PRIMARY",
        "youtube_playlist",
        0,
        BARI_UNRESOLVED + f" Target lecture: {watch_hint}.",
    )


def bari_video(slug, title, url, order=0):
    return r(
        f"{slug}-primary",
        title,
        url,
        "Abdul Bari",
        "PRIMARY",
        "youtube_video",
        order,
        "Official Abdul Bari video (author verified via YouTube oEmbed).",
    )


def mit_dd(slug, title, url):
    return r(
        f"{slug}-mit",
        title,
        url,
        "MIT OCW 6.006",
        "DEEP_DIVE",
        "documentation",
        3,
        "Optional MIT 6.006 lecture page. Not mandatory. Do not complete the entire course.",
    )


def nc150(slug, category):
    return r(
        f"{slug}-nc150",
        f"NeetCode 150 — {category} (representative subset)",
        NC_150,
        "NeetCode",
        "PRACTICE",
        "coding_problem",
        1,
        f"Open the {category} section. Solve only the small representative subset listed in the exercise — not all 150.",
    )


def nccore(slug, item):
    return r(
        f"{slug}-nccore",
        f"NeetCode Core Skills — {item}",
        NC_CORE,
        "NeetCode",
        "PRACTICE",
        "coding_problem",
        2,
        f"Implement {item} from Core Skills. Java primary. This is implementation, not video mastery.",
    )


def lc_collection(slug):
    return r(
        f"{slug}-lcplan",
        "LeetCode Study Plans (collection)",
        LC_PLAN,
        "LeetCode",
        "PRACTICE",
        "coding_problem",
        4,
        "Official study-plan hub. Individual problem slugs were not verified here (Cloudflare 403). "
        "Use NeetCode 150 as the verified problem list; treat LeetCode as optional transfer if you already know a slug.",
    )


CPP = {
    "array": "Java int[] / ArrayList ≈ C++ vector (ArrayList grows; raw arrays are fixed).",
    "string": "Java String is immutable; StringBuilder ≈ C++ string mutation. Do not redo Domain 1 syntax.",
    "map": "Java HashMap ≈ C++ unordered_map; TreeMap ≈ map.",
    "set": "Java HashSet ≈ C++ unordered_set; TreeSet ≈ set.",
    "deque": "Java ArrayDeque ≈ C++ deque. Prefer ArrayDeque over legacy java.util.Stack.",
    "heap": "Java PriorityQueue is a min-heap by default. C++ priority_queue is a max-heap by default. Invert with Comparator / greater<>.",
    "node": "Java Node.next is a reference; C++ is typically Node*. Same aliasing/mutation model.",
    "cmp": "Java Comparator/Comparable ≈ C++ comparator / operator<. Heap module depends on this Java knowledge.",
}
