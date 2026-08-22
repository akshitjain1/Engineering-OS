"""Helpers and verified URLs for Domain 1 Java authoring. No invented URLs."""

from __future__ import annotations

HELSINKI_NOTE = (
    "University of Helsinki Java Programming I/II is the exercise-heavy layer. "
    "It is a legacy, unmaintained course (historically JDK 11 and NetBeans/TMC). "
    "Do not treat that toolchain as required. Complete the same exercises with a current JDK "
    "using javac/java, JShell, or an IDE of your choice. Dev.java is the authoritative modern reference."
)

DSA_METHODS = (
    "DSA connection: after this topic, Domain 2 may depend on Java methods. "
    "Streams, lambdas, concurrency, and JVM topics are not DSA gates."
)
DSA_ARRAYS = (
    "DSA connection: Domain 2 array patterns (traversal, two pointers, prefix sums) use this language foundation. "
    "This topic is Java arrays, not the DSA module."
)
DSA_STRINGS = "DSA connection: Domain 2 string problems use Java String and character processing."
DSA_REFS = (
    "DSA connection: linked lists, trees, and graphs in Domain 2 depend on classes plus reference/aliasing semantics. "
    "Java is pass-by-value; the value copied for objects is the reference."
)
DSA_LIST = "DSA connection: ArrayList is the usual Java stand-in for a resizable array / C++ vector."
DSA_SET = "DSA connection: HashSet is used heavily for uniqueness and hashing problems. C++ analogue: unordered_set."
DSA_MAP = "DSA connection: HashMap is used heavily for hashing, frequency, and graphs. C++ analogue: unordered_map."
DSA_HEAP = (
    "DSA connection: heaps in Domain 2 use PriorityQueue plus Comparable/Comparator. "
    "C++ analogue: priority_queue."
)


def r(slug, title, url, provider, role, rtype, order, description, duration=None):
    item = {
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
    if duration is not None:
        item["duration"] = duration
    return item


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


def ex(slug, title, instructions, difficulty="beginner", order=0):
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


# Helsinki — verified part/section pages (trailing slash as served).
H = "https://java-programming.mooc.fi"
H_HOME = f"{H}/"
H_P1 = f"{H}/part-1/"
H_P1_START = f"{H}/part-1/1-starting-programming/"
H_P1_PRINT = f"{H}/part-1/2-printing/"
H_P1_READ = f"{H}/part-1/3-reading/"
H_P1_VAR = f"{H}/part-1/4-variables/"
H_P1_CALC = f"{H}/part-1/5-calculating/"
H_P1_COND = f"{H}/part-1/6-conditional-statements/"
H_P2 = f"{H}/part-2/"
H_P2_REPEAT = f"{H}/part-2/2-repeating/"
H_P2_LOOPS = f"{H}/part-2/3-more-loops/"
H_P2_METHODS = f"{H}/part-2/4-methods/"
H_P3_LISTS = f"{H}/part-3/2-lists/"
H_P3_ARRAYS = f"{H}/part-3/3-arrays/"
H_P3_STRINGS = f"{H}/part-3/4-using-strings/"
H_P4_OOP = f"{H}/part-4/1-introduction-to-object-oriented-programming/"
H_P4_FILES = f"{H}/part-4/3-files-and-reading-data/"
H_P5_OOP = f"{H}/part-5/1-learning-object-oriented-programming/"
H_P5_OVER = f"{H}/part-5/2-method-and-constructor-overloading/"
H_P5_PRIMREF = f"{H}/part-5/3-primitive-and-reference-variables/"
H_P5_OBJREF = f"{H}/part-5/4-objects-and-references/"
H_P6_WITHIN = f"{H}/part-6/1-objects-within-objects/"
H_P6_UI = f"{H}/part-6/2-separating-user-interface-from-program-logic/"
H_P6_TEST = f"{H}/part-6/3-introduction-to-testing/"
H_P8_MAP = f"{H}/part-8/2-hash-map/"
H_P8_GROUP = f"{H}/part-8/4-grouping-data-using-hash-maps/"
H_P9_INH = f"{H}/part-9/1-inheritance/"
H_P9_IFACE = f"{H}/part-9/2-interface/"
H_P9_POLY = f"{H}/part-9/3-object-polymorphism/"
H_P10_STREAM = f"{H}/part-10/1-handling-collections-as-streams/"
H_P10_COMP = f"{H}/part-10/2-interface-comparable/"
H_P11_PKG = f"{H}/part-11/2-packages/"
H_P11_EX = f"{H}/part-11/3-exceptions/"
H_P11_FILES = f"{H}/part-11/4-processing-files/"
H_P12_GEN = f"{H}/part-12/1-type-parameters/"
H_P12_MULTI = f"{H}/part-12/4-multidimensional-data/"
H_P14_MAVEN = f"{H}/part-14/4-maven-and-third-party-libraries/"

# Dev.java — verified tutorial pages.
DJ_GET = "https://dev.java/learn/getting-started/"
DJ_LAUNCH = "https://dev.java/learn/launch-simple-source-code-programs/"
DJ_JSHELL = "https://dev.java/learn/jshell-tool/"
DJ_VSCODE = "https://dev.java/learn/vscode-java/"
DJ_VAR = "https://dev.java/learn/language-basics/variables/"
DJ_PRIM = "https://dev.java/learn/language-basics/primitive-types/"
DJ_ARR = "https://dev.java/learn/language-basics/arrays/"
DJ_USING_VAR = "https://dev.java/learn/language-basics/using-var/"
DJ_OPS = "https://dev.java/learn/language-basics/using-operators/"
DJ_ALL_OPS = "https://dev.java/learn/language-basics/all-operators/"
DJ_FLOW = "https://dev.java/learn/language-basics/controlling-flow/"
DJ_SWITCH = "https://dev.java/learn/language-basics/switch-statement/"
DJ_SWITCH_EXPR = "https://dev.java/learn/language-basics/switch-expression/"
DJ_STRINGS = "https://dev.java/learn/numbers-strings/strings/"
DJ_SB = "https://dev.java/learn/numbers-strings/string-builders/"
DJ_CHARS = "https://dev.java/learn/numbers-strings/characters/"
DJ_AUTOBOX = "https://dev.java/learn/numbers-strings/autoboxing/"
DJ_CLASS = "https://dev.java/learn/classes-objects/creating-classes/"
DJ_OBJ = "https://dev.java/learn/classes-objects/creating-objects/"
DJ_CTOR = "https://dev.java/learn/classes-objects/defining-constructors/"
DJ_METH = "https://dev.java/learn/classes-objects/defining-methods/"
DJ_CALL = "https://dev.java/learn/classes-objects/calling-methods-constructors/"
DJ_MORE = "https://dev.java/learn/classes-objects/more-on-classes/"
DJ_DESIGN = "https://dev.java/learn/classes-objects/design-best-practices/"
DJ_INH = "https://dev.java/learn/inheritance/what-is-inheritance/"
DJ_OVERRIDE = "https://dev.java/learn/inheritance/overriding/"
DJ_POLY = "https://dev.java/learn/inheritance/polymorphism/"
DJ_ABS = "https://dev.java/learn/inheritance/abstract-classes/"
DJ_IFACE = "https://dev.java/learn/interfaces/defining-interfaces/"
DJ_IFACE_TYPE = "https://dev.java/learn/interfaces/interfaces-as-a-type/"
DJ_GEN = "https://dev.java/learn/generics/intro/"
DJ_WILD = "https://dev.java/learn/generics/wildcards/"
DJ_ERASE = "https://dev.java/learn/generics/type-erasure/"
DJ_FI = "https://dev.java/learn/lambdas/functional-interfaces/"
DJ_LAM = "https://dev.java/learn/lambdas/first-lambdas/"
DJ_MREF = "https://dev.java/learn/lambdas/method-references/"
DJ_COMP_LAM = "https://dev.java/learn/lambdas/writing-comparators/"
DJ_EX_WHAT = "https://dev.java/learn/exceptions/what-is-an-exception/"
DJ_EX_CATCH = "https://dev.java/learn/exceptions/catching-handling/"
DJ_EX_THROW = "https://dev.java/learn/exceptions/throwing/"
DJ_PKG = "https://dev.java/learn/packages/"
DJ_COL_INTRO = "https://dev.java/learn/api/collections-framework/intro/"
DJ_LISTS = "https://dev.java/learn/api/collections-framework/lists/"
DJ_SETS = "https://dev.java/learn/api/collections-framework/sets/"
DJ_MAPS = "https://dev.java/learn/api/collections-framework/maps/"
DJ_ITER = "https://dev.java/learn/api/collections-framework/iterating/"
DJ_AL_LL = "https://dev.java/learn/api/collections-framework/arraylist-vs-linkedlist/"
DJ_QQ = "https://dev.java/learn/api/collections-framework/stacks-queues/"
DJ_STREAMS = "https://dev.java/learn/api/streams/"
DJ_MFR = "https://dev.java/learn/api/streams/map-filter-reduce/"
DJ_INTER = "https://dev.java/learn/api/streams/intermediate-operation/"
DJ_TERM = "https://dev.java/learn/api/streams/terminal-operations/"
DJ_IO = "https://dev.java/learn/java-io/"
DJ_IO_FS = "https://dev.java/learn/java-io/file-system/"
DJ_IO_RW = "https://dev.java/learn/java-io/reading-writing/"
DJ_IO_INTRO = "https://dev.java/learn/java-io/intro/"
DJ_JAVAC = "https://dev.java/learn/jvm/tools/core/javac/"
DJ_JAVA = "https://dev.java/learn/jvm/tools/core/java/"
DJ_JAVAP = "https://dev.java/learn/jvm/tools/core/javap/"
DJ_GC = "https://dev.java/learn/jvm/tool/garbage-collection/"
DJ_VT = "https://dev.java/learn/new-features/virtual-threads/"
DJ_DBG = "https://dev.java/learn/debugging/"
DJ_PM = "https://dev.java/learn/pattern-matching/"

JUNIT = "https://junit.org/junit5/docs/current/user-guide/"
ORACLE_CONC = "https://docs.oracle.com/javase/tutorial/essential/concurrency/"
PQ_API = "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html"
CMP_API = "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Comparable.html"
