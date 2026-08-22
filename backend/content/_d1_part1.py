"""Domain 1: Getting Started through Methods."""

from __future__ import annotations

from _d1_helpers import (
    DJ_ALL_OPS,
    DJ_ARR,
    DJ_AUTOBOX,
    DJ_CALL,
    DJ_FLOW,
    DJ_GET,
    DJ_JAVA,
    DJ_JAVAC,
    DJ_JSHELL,
    DJ_LAUNCH,
    DJ_METH,
    DJ_OPS,
    DJ_PRIM,
    DJ_SWITCH,
    DJ_SWITCH_EXPR,
    DJ_USING_VAR,
    DJ_VAR,
    DJ_VSCODE,
    DSA_METHODS,
    H_P1_CALC,
    H_P1_COND,
    H_P1_PRINT,
    H_P1_READ,
    H_P1_START,
    H_P1_VAR,
    H_P2_LOOPS,
    H_P2_METHODS,
    H_P2_REPEAT,
    H_P5_OVER,
    HELSINKI_NOTE,
    ex,
    q,
    r,
    unit,
)

CONTENT = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


_add(
    "java-jdk-jre",
    hours=0.75,
    objective="Install a current JDK and explain JDK vs JRE vs JVM.",
    explanation=(
        "The JDK (Java Development Kit) is what you install to compile and run Java. "
        "The JVM (Java Virtual Machine) executes bytecode. A JRE was historically a runtime-only subset; "
        "modern OpenJDK/Oracle distributions emphasize the JDK. You write .java source, javac (or the Java launcher) "
        "produces .class bytecode, and the JVM runs it. "
        "Helsinki's setup still mentions older NetBeans/TMC tooling — that is not required. "
        "Verify `java -version` and `javac -version` on your machine. IDE choice is optional (VS Code is fine)."
    ),
    mastery=[
        "Explain JDK vs JVM vs historical JRE without notes.",
        "Install or locate a JDK and print java/javac versions.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-jdk-jre-primary", "Getting Started with Java (JDK setup)", DJ_GET, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Modern JDK download/setup, compilation cycle, and first program. Authoritative for tooling."),
        r("java-jdk-jre-reference", "javac — Core JDK tools", DJ_JAVAC, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Official javac tool page."),
        r("java-jdk-jre-practice", "Helsinki Part 1 — Getting started", H_P1_START, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 2,
          HELSINKI_NOTE + " Use the programming-environment exercises; ignore NetBeans as a mandate."),
    ],
    questions=[
        q("java-jdk-jre-q1",
          "Why does a Java developer typically install a JDK rather than a historical JRE?",
          ["A JRE can compile .java files but cannot run them.",
           "A JDK includes the compiler and other development tools; a JRE was runtime-only.",
           "The JVM only exists inside a JRE, never inside a JDK.",
           "A JDK is required only for Android, not for console Java."],
          "A JDK includes the compiler and other development tools; a JRE was runtime-only.",
          "You need javac (or equivalent) to build. Runtime-only bundles were for running already-built apps.",
          mastery=True),
        q("java-jdk-jre-q2",
          "What does the JVM actually execute?",
          ["C++ object files produced by javac.",
           "Raw .java text, interpreted line by line like a shell script.",
           "Bytecode, typically stored in .class files.",
           "SQL stored procedures generated from annotations."],
          "Bytecode, typically stored in .class files.",
          "javac translates source to bytecode; the JVM loads and executes that bytecode."),
        q("java-jdk-jre-q3",
          "You run `java -version` successfully but `javac -version` is not found. What is the most likely situation?",
          ["The JVM is missing but the compiler is installed.",
           "A runtime is on PATH, but the compiler from a JDK is not.",
           "Your source file has a syntax error.",
           "You must install Maven before javac exists."],
          "A runtime is on PATH, but the compiler from a JDK is not.",
          "java can exist without javac if only a runtime is installed or PATH points at the wrong bin."),
        q("java-jdk-jre-q4",
          "Is a specific IDE required to learn this Java curriculum?",
          ["Yes: only NetBeans with TMC is valid.",
           "Yes: only IntelliJ Ultimate is valid.",
           "No: javac/java, JShell, or any IDE that uses a JDK is acceptable.",
           "Yes: VS Code is mandatory because the user uses it."],
          "No: javac/java, JShell, or any IDE that uses a JDK is acceptable.",
          "VS Code is convenient here but not a conceptual requirement. Helsinki's NetBeans path is legacy."),
    ],
    exercises=[
        ex("java-jdk-jre-ex1", "Verify the JDK",
           "Install or locate a current JDK. From a terminal, run `java -version` and `javac -version` and save the output. "
           "Write three sentences: what the JDK is, what the JVM is, and why a historical JRE would be insufficient for compiling. "
           "If you use an IDE (optional), point it at the same JDK. Do not treat NetBeans as required."),
    ],
)

_add(
    "java-first-program",
    hours=0.5,
    objective="Write, compile, and run a single-class Java program with a main method.",
    explanation=(
        "A first Java application is a class with `public static void main(String[] args)`. "
        "The file name should match the public class. Printing uses System.out. "
        "Starting with recent JDKs you can also launch a `.java` source file directly; still learn the class/main shape "
        "because DSA and interviews expect it. Do not complete Helsinki as a beginner-from-zero course — use the first print exercises as reps."
    ),
    mastery=[
        "Write a Hello World class independently.",
        "Explain what main is for.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-first-program-primary", "Helsinki Part 1 — Printing", H_P1_PRINT, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Printing and first programs."),
        r("java-first-program-reference", "Getting Started with Java", DJ_GET, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Modern first-class / first-application walkthrough."),
        r("java-first-program-practice", "JShell — The Java Shell Tool", DJ_JSHELL, "Dev.java",
          "PRACTICE", "documentation", 2,
          "Use JShell to evaluate small expressions without a full class when exploring syntax."),
    ],
    questions=[
        q("java-first-program-q1",
          "Why does a typical Java application declare `public static void main(String[] args)`?",
          ["The JVM looks for this method as the program entry point.",
           "main is required on every class, including helper classes.",
           "args must be named args or the program will not compile.",
           "void means the method prints automatically."],
          "The JVM looks for this method as the program entry point.",
          "static lets the JVM call it without constructing an object first.",
          mastery=True),
        q("java-first-program-q2",
          "A public class is named Greeter. What should the source file usually be called?",
          ["greeter.java", "Main.java", "Greeter.java", "Greeter.class"],
          "Greeter.java",
          "A public class name matches the file name. .class is compiler output."),
        q("java-first-program-q3",
          "What is JShell useful for at this stage?",
          ["Shipping production services.",
           "Quickly evaluating expressions and snippets without writing a full class each time.",
           "Replacing the JVM.",
           "Compiling C++ DSA code."],
          "Quickly evaluating expressions and snippets without writing a full class each time.",
          "JShell is a REPL. Real programs still use classes and main (or an application framework later)."),
        q("java-first-program-q4",
          "Does watching a getting-started page mark this topic mastered?",
          ["Yes, if the page is official.",
           "Yes, if Helsinki's first video is finished.",
           "No: mastery requires writing and running a program plus the questions.",
           "Yes, if you starred the repository."],
          "No: mastery requires writing and running a program plus the questions.",
          "A resource is not mastery."),
    ],
    exercises=[
        ex("java-first-program-ex1", "Hello, then JShell",
           "Create Greeter.java with a main method that prints two lines (your name and a short goal for Java). "
           "Compile and run it. Then open JShell and evaluate 3 + 4 * 2; explain why the result matches operator precedence. "
           "Optional: open the same file in VS Code using the Java extension — not required."),
    ],
)

_add(
    "java-compile-and-run",
    hours=0.75,
    objective="Use javac/java (or equivalent) reliably and explain .java vs .class.",
    explanation=(
        "javac compiles source to bytecode (.class). java launches the JVM against a class name (not the .java file name with extension, "
        "unless you use source-file mode). Modern JDKs can run `java Hello.java` for simple programs. "
        "You still need to understand classpath and that the launcher loads classes. "
        "This compile-run loop is the tooling for the rest of Java and for running DSA solutions."
    ),
    mastery=[
        "Explain .java vs .class vs the java launcher.",
        "Compile and run from the command line at least once.",
        "Inspect that a .class file was produced.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-compile-and-run-primary", "Launching simple source-code programs", DJ_LAUNCH, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Modern java launcher, including running .java source files."),
        r("java-compile-and-run-reference", "java launcher — Core JDK tools", DJ_JAVA, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Official java tool page."),
        r("java-compile-and-run-practice", "Helsinki Part 1 — Getting started", H_P1_START, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 2,
          HELSINKI_NOTE + " Environment exercises; map them onto javac/java or your IDE run button."),
    ],
    questions=[
        q("java-compile-and-run-q1",
          "After `javac Hello.java`, what do you typically pass to `java`?",
          ["Hello.java", "Hello.class", "Hello", "./Hello.exe"],
          "Hello",
          "The launcher wants the class name. Hello.class is the file; Hello.java is source.",
          mastery=True),
        q("java-compile-and-run-q2",
          "What is source-file mode (`java Hello.java`) for?",
          ["Replacing the JVM with an interpreter that never uses bytecode.",
           "Conveniently compiling and launching simple programs in one step.",
           "Running .class files that lost their source.",
           "Linking C++ object files into a JAR."],
          "Conveniently compiling and launching simple programs in one step.",
          "It is a launcher convenience. Larger projects still use a build tool and class/JAR output."),
        q("java-compile-and-run-q3",
          "Why might `java Hello` fail with a class-not-found error even though Hello.java is in the folder?",
          ["You must rename the file to main.java.",
           "The JVM only runs files with a .exe extension.",
           "You are in the wrong directory, the class was not compiled, or the package/classpath does not match.",
           "System.out is not imported."],
          "You are in the wrong directory, the class was not compiled, or the package/classpath does not match.",
          "The launcher loads classes from the classpath, not by magically finding any nearby source file."),
        q("java-compile-and-run-q4",
          "What should you look at to confirm compilation happened?",
          ["A Git commit message.",
           "A .class file (or build output) produced from the source.",
           "The presence of a JRE installer on the desktop.",
           "A passing Helsinki quiz without running code."],
          "A .class file (or build output) produced from the source.",
          "Bytecode on disk (or in a build directory) is the compile artifact."),
        q("java-compile-and-run-q5",
          "VS Code Java workflow is:",
          ["Mandatory for every exercise in this domain.",
           "An optional way to compile, run, and debug using the same JDK.",
           "A replacement for understanding javac/java.",
           "The only way to use JShell."],
          "An optional way to compile, run, and debug using the same JDK.",
          "Dev.java documents VS Code Java; it is not a curriculum gate."),
    ],
    exercises=[
        ex("java-compile-and-run-ex1", "Compile, run, inspect",
           "Write CompileDemo.java that prints one line. Run `javac CompileDemo.java`, confirm CompileDemo.class exists, then `java CompileDemo`. "
           "Run once with `java CompileDemo.java` if your JDK supports source-file mode. Note any difference in artifacts. "
           "Optional: set a breakpoint in VS Code and step over the print. Record JDK version used."),
    ],
)

_add(
    "java-primitives",
    hours=0.75,
    objective="Declare, initialize, and choose Java primitive types; distinguish them from String and other references.",
    explanation=(
        "Java primitives are boolean, byte, short, int, long, float, double, and char. They are not objects. "
        "String is a reference type (a class), even though it has literals. "
        "`var` infers a type from the initializer; it is not a dynamic type. "
        "Uninitialized local variables cannot be read. Prefer explicit types while learning; use var when the type is obvious."
    ),
    mastery=[
        "List the primitive types and contrast them with String.",
        "Choose types for integers, floating values, flags, and characters.",
        "Explain what var does and does not do.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-primitives-primary", "Helsinki Part 1 — Variables", H_P1_VAR, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Variable declaration and first typed values."),
        r("java-primitives-reference", "Creating primitive type variables", DJ_PRIM, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Authoritative primitive-type syntax and initialization."),
        r("java-primitives-deep", "Using the var type identifier", DJ_USING_VAR, "Dev.java",
          "DEEP_DIVE", "documentation", 2,
          "Local-variable type inference. Not a substitute for understanding actual types."),
    ],
    questions=[
        q("java-primitives-q1",
          "Which statement is true?",
          ["String is a primitive type like int.",
           "int is a primitive; String is a reference to an object.",
           "boolean is stored as a String of \"true\" or \"false\".",
           "char and String are the same type."],
          "int is a primitive; String is a reference to an object.",
          "Primitives are not objects. String lives on the heap as an object.",
          mastery=True),
        q("java-primitives-q2",
          "What happens if you read a local `int x;` with no initializer?",
          ["It is 0.", "It is null.", "The code does not compile.", "It is a random leftover value like C."],
          "The code does not compile.",
          "Java local variables must be definitely assigned before use."),
        q("java-primitives-q3",
          "`var n = 3;` — what is n's type?",
          ["Object", "var", "int", "Integer always"],
          "int",
          "var infers int from the integer literal. var is not a runtime type."),
        q("java-primitives-q4",
          "Why is `double` a better default than `float` for most application math?",
          ["float cannot represent fractions.",
           "double is the default floating type in Java literals like 1.0 and usually has more precision.",
           "float is deprecated.",
           "double is a reference type and therefore safer."],
          "double is the default floating type in Java literals like 1.0 and usually has more precision.",
          "Use float only when you have a reason (memory, APIs)."),
        q("java-primitives-q5",
          "Which type stores a single UTF-16 code unit?",
          ["byte", "boolean", "char", "String"],
          "char",
          "char is a 16-bit numeric type. A full Unicode character may need a surrogate pair or a String."),
    ],
    exercises=[
        ex("java-primitives-ex1", "Type conversion notebook",
           "Write TypesDemo with locals of each primitive plus a String. Print their values. "
           "Add `var inferred = 42;` and print inferred's value. "
           "In comments, state which of those variables are primitives vs references. "
           "Then write a tiny utility method that takes an int minutes and returns a double hours (minutes / 60.0)."),
    ],
)

_add(
    "java-type-conversion",
    hours=0.5,
    objective="Apply widening and narrowing conversions and explain overflow.",
    explanation=(
        "Widening conversions (int → long → float → double) can be implicit. Narrowing (double → int, long → int) needs a cast and can truncate. "
        "Integer overflow wraps in two's complement; it does not throw. Mixing int division (`5 / 2`) truncates. "
        "Boxing (int ↔ Integer) is separate from primitive widening — see autoboxing later when you use collections."
    ),
    mastery=[
        "Predict implicit vs explicit conversion.",
        "Explain one overflow and one integer-division surprise.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-type-conversion-primary", "Helsinki Part 1 — Calculating with numbers", H_P1_CALC, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Arithmetic and numeric calculations; watch integer division."),
        r("java-type-conversion-reference", "Primitive types", DJ_PRIM, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Primitive declarations; combine with the internal lesson on widening/narrowing."),
        r("java-type-conversion-deep", "Autoboxing and unboxing", DJ_AUTOBOX, "Dev.java",
          "DEEP_DIVE", "documentation", 2,
          "Primitive vs wrapper conversions. Collections store wrappers, not raw ints."),
    ],
    questions=[
        q("java-type-conversion-q1",
          "What does `(int) 3.9` evaluate to?",
          ["4", "3", "3.9", "compile error"],
          "3",
          "Casting toward int truncates toward zero; it does not round.",
          mastery=True),
        q("java-type-conversion-q2",
          "What is `1_000_000 * 1_000_000` if both are int?",
          ["10^12 exactly as an int.",
           "An overflowed int; the mathematical product does not fit in 32 bits.",
           "A compile error because underscores are illegal.",
           "Automatically promoted to long."],
          "An overflowed int; the mathematical product does not fit in 32 bits.",
          "int arithmetic wraps. Use long literals (1_000_000L) when the product needs 64 bits."),
        q("java-type-conversion-q3",
          "Why is `5 / 2` equal to 2 rather than 2.5?",
          ["Java cannot represent 2.5.",
           "Both operands are ints, so the division is integer division.",
           "Operator / always truncates, even for doubles.",
           "You forgot to import Math."],
          "Both operands are ints, so the division is integer division.",
          "Write 5 / 2.0 or cast to get floating division."),
        q("java-type-conversion-q4",
          "Assigning an int to a long without a cast is allowed because:",
          ["long is smaller than int.",
           "It is a widening conversion that cannot overflow the destination type.",
           "The compiler always inserts a runtime check.",
           "int and long are the same size."],
          "It is a widening conversion that cannot overflow the destination type.",
          "Every int value fits in a long."),
    ],
    exercises=[
        ex("java-type-conversion-ex1", "Predict, then run",
           "On paper, predict: (1) `5 / 2`, (2) `5 / 2.0`, (3) `(int) (5 / 2.0)`, (4) `Integer.MAX_VALUE + 1`. "
           "Then write ConvertDemo that prints the actual results. Explain each mismatch in comments. "
           "Add a method `safeHours(int minutes)` that returns a double using 60.0, not 60."),
    ],
)

_add(
    "java-console-io",
    hours=1.0,
    objective="Read console input, validate it, and print formatted results in a small interactive loop.",
    explanation=(
        "Console programs write with System.out (print/printf) and read with java.util.Scanner or similar. "
        "Always validate: empty lines, non-numeric text, and out-of-range values. "
        "Do not obsess over Scanner internals. Helsinki Part 1 reading exercises are the practice layer. "
        "Build a tiny CLI: prompt → parse → compute → repeat until quit."
    ),
    mastery=[
        "Read strings and numbers from stdin.",
        "Reject invalid input without crashing.",
        "Build a small interactive loop.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-console-io-primary", "Helsinki Part 1 — Reading input", H_P1_READ, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Scanner-based console input exercises."),
        r("java-console-io-practice", "Helsinki Part 1 — Calculating with numbers", H_P1_CALC, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 1,
          "Combine reading with numeric calculation. Still legacy tooling; run locally with a current JDK."),
    ],
    questions=[
        q("java-console-io-q1",
          "Scanner.nextLine() after nextInt() often surprises beginners because:",
          ["nextInt consumes the rest of the line including the leftover newline in a way that skips the next nextLine.",
           "Scanner cannot read integers.",
           "System.in can only be read once per JVM.",
           "printf disables Scanner."],
          "nextInt consumes the rest of the line including the leftover newline in a way that skips the next nextLine.",
          "Prefer consistent nextLine + parse, or consume the leftover newline after nextInt.",
          mastery=True),
        q("java-console-io-q2",
          "What should a CLI do when the user types \"abc\" where an int is required?",
          ["Let the program crash with InputMismatchException uncaught.",
           "Catch/validate, explain the error, and re-prompt.",
           "Silently treat it as 0.",
           "Restart the JVM."],
          "Catch/validate, explain the error, and re-prompt.",
          "Validation is part of I/O, not an advanced topic."),
        q("java-console-io-q3",
          "printf vs println:",
          ["printf can format numbers and strings with format specifiers; println prints a line as-is.",
           "println is deprecated.",
           "printf writes to a file only.",
           "They are identical."],
          "printf can format numbers and strings with format specifiers; println prints a line as-is.",
          "Use either; formatted output is useful for tables and money-like displays."),
        q("java-console-io-q4",
          "Why keep the prompt/parse/print loop small?",
          ["Java forbids methods during I/O.",
           "So you can later extract parsing into methods (the DSA gate) without a 200-line main.",
           "Scanner only works in main.",
           "Helsinki graders reject methods."],
          "So you can later extract parsing into methods (the DSA gate) without a 200-line main.",
          "I/O is a place to practice structure, not only Scanner calls."),
    ],
    exercises=[
        ex("java-console-io-ex1", "Interactive calculator CLI",
           "Write a loop that: (1) prompts for an operation (add/sub/mul/div/quit), (2) reads two numbers, "
           "(3) prints the result with printf, (4) on invalid operation or non-numeric input, prints a clear error and continues. "
           "Reject division by zero. Do not crash. This is the I/O exercise, not a Scanner internals report. "
           + HELSINKI_NOTE,
           difficulty="intermediate"),
    ],
)

_add(
    "java-operators",
    hours=0.75,
    objective="Predict arithmetic, comparison, logical, assignment, increment, ternary, and short-circuit behavior.",
    explanation=(
        "Operators combine values. Precedence and associativity matter; when unclear, use parentheses. "
        "`&&` and `||` short-circuit: the right operand may not run. "
        "`++i` vs `i++` differs when the value is used in a larger expression. "
        "The ternary `cond ? a : b` is an expression. Assignment is `=`; equality is `==` (for primitives)."
    ),
    mastery=[
        "Evaluate mixed expressions on paper, then verify in code.",
        "Explain short-circuit evaluation with an example.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-operators-primary", "Using operators", DJ_OPS, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Authoritative operator tutorial."),
        r("java-operators-reference", "Helsinki Part 1 — Calculating with numbers", H_P1_CALC, "University of Helsinki",
          "REFERENCE", "interactive_tutorial", 1,
          HELSINKI_NOTE + " Numeric operator practice."),
        r("java-operators-deep", "Wrapping up the Java operators", DJ_ALL_OPS, "Dev.java",
          "DEEP_DIVE", "documentation", 2,
          "Full operator set when you need a catalog. Do not memorize every bitwise operator yet."),
    ],
    questions=[
        q("java-operators-q1",
          "What does `3 + 4 * 2` evaluate to?",
          ["14", "11", "10", "24"],
          "11",
          "* binds tighter than +. Parentheses would change it.",
          mastery=True),
        q("java-operators-q2",
          "`false && (1/0 == 0)` — why does this not throw?",
          ["Division by zero is legal on ints.",
           "&& short-circuits: the right operand is not evaluated.",
           "The compiler rewrites it to false && false.",
           "Java catches ArithmeticException automatically."],
          "&& short-circuits: the right operand is not evaluated.",
          "|| similarly skips the right side when the left is true."),
        q("java-operators-q3",
          "int i = 1; what is `i++ + ++i`? (Predict carefully, then verify.)",
          ["Always 2.",
           "The result is well-defined but easy to misread; you should not write this in real code.",
           "It does not compile.",
           "It is undefined behavior like C++."],
          "The result is well-defined but easy to misread; you should not write this in real code.",
          "Java defines the order, but interviewers and teammates hate this. Prefer i += 1; separately."),
        q("java-operators-q4",
          "Ternary `x >= 0 ? x : -x` is best described as:",
          ["A loop.", "An expression that yields the absolute value for ints (except Integer.MIN_VALUE).",
           "A statement that cannot be assigned.", "A replacement for methods."],
          "An expression that yields the absolute value for ints (except Integer.MIN_VALUE).",
          "Integer.MIN_VALUE's negation overflows; note that as an edge."),
        q("java-operators-q5",
          "Why is `=` not the same as `==`?",
          ["They are aliases.",
           "`=` assigns; `==` compares primitives (and object identity for references).",
           "`==` assigns to constants only.",
           "`=` only works on Strings."],
          "`=` assigns; `==` compares primitives (and object identity for references).",
          "String content comparison is later (.equals)."),
    ],
    exercises=[
        ex("java-operators-ex1", "Expression lab",
           "Write OperatorsLab that prints the value of: `3 + 4 * 2`, `(3 + 4) * 2`, `true || (1/0==0)`, `false && (1/0==0)`, "
           "and a ternary that picks the max of two ints without Math.max. "
           "For each, write a one-line comment predicting the result before you run. Fix comments if you were wrong."),
    ],
)

_add(
    "java-if-else",
    hours=0.5,
    objective="Branch with if/else, including nested conditions, without unreadable ladders.",
    explanation=(
        "if/else chooses a path from a boolean. Nesting is legal but deep nesting is a smell — extract methods or invert conditions. "
        "Brace style: always use braces for bodies you will maintain. Helsinki conditionals are the exercise set."
    ),
    mastery=[
        "Write if/else with clear boolean conditions.",
        "Avoid a 4-level nest by restructuring.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-if-else-primary", "Helsinki Part 1 — Conditional statements", H_P1_COND, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " if/else exercises."),
        r("java-if-else-reference", "Control flow statements", DJ_FLOW, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Decision, loop, and branch statements. Use the if/else portions."),
    ],
    questions=[
        q("java-if-else-q1",
          "if (score >= 90) A; else if (score >= 80) B; else C; — score 80 prints:",
          ["A", "B", "C", "A and B"],
          "B",
          "The first true branch wins; 80 fails >= 90 and matches >= 80.",
          mastery=True),
        q("java-if-else-q2",
          "Why can `if (x = 1)` fail to compile when x is int?",
          ["Assignment is illegal in Java.",
           "The condition must be boolean; `x = 1` is an int.",
           "1 is not a valid int.",
           "You must use switch."],
          "The condition must be boolean; `x = 1` is an int.",
          "Unlike C, Java does not treat ints as booleans. `if (x == 1)` compares."),
        q("java-if-else-q3",
          "A better alternative to five nested ifs for disjoint ranges is often:",
          ["Deeper nesting.", "else-if chain or a well-named method per rule.",
           "busy-wait loop.", "catching Exception."],
          "else-if chain or a well-named method per rule.",
          "Structure first; switch comes next for discrete values."),
        q("java-if-else-q4",
          "What does an if without else mean if the condition is false?",
          ["The program stops.", "The then-body is skipped and execution continues.",
           "Java inserts an implicit else throw.", "It does not compile."],
          "The then-body is skipped and execution continues.",
          "else is optional."),
    ],
    exercises=[
        ex("java-if-else-ex1", "Grade and validate",
           "Read an integer 0–100. Print a letter grade. If the input is outside 0–100, print an error and ask again (loop from the I/O topic). "
           "Then refactor the grade decision into a method `letterGrade(int score)` that returns a String. "
           + HELSINKI_NOTE),
    ],
)

_add(
    "java-switch",
    hours=0.75,
    objective="Use switch statements and modern switch expressions; know when if/else is clearer.",
    explanation=(
        "Classic switch statements jump on a discrete value and historically needed break to avoid fall-through. "
        "Modern switch expressions (`switch (x) { case 1 -> \"a\"; default -> \"b\"; }`) yield a value and do not fall through. "
        "Helsinki predates much of this: treat Dev.java as authoritative. Do not memorize every preview feature; statements vs expressions is the core."
    ),
    mastery=[
        "Write a switch expression for a small menu.",
        "Explain fall-through vs arrow cases.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-switch-primary", "Branching with switch statements", DJ_SWITCH, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Classic switch. Note break and fall-through."),
        r("java-switch-reference", "Branching with switch expressions", DJ_SWITCH_EXPR, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Modern switch as an expression. Prefer this for new code when the JDK supports it."),
        r("java-switch-practice", "Helsinki Part 1 — Conditional statements", H_P1_COND, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 2,
          HELSINKI_NOTE + " Conditionals practice; implement the menu with modern switch locally even if Helsinki shows if/else."),
    ],
    questions=[
        q("java-switch-q1",
          "In a classic switch, forgetting break typically causes:",
          ["A compile error always.", "Fall-through into the next case.",
           "The JVM to crash.", "Automatic return."],
          "Fall-through into the next case.",
          "Arrow `case L ->` form does not fall through.",
          mastery=True),
        q("java-switch-q2",
          "A switch expression must:",
          ["Omit default even when the type is String.",
           "Cover all possibilities (or have default) so it always yields a value.",
           "Use only integers.",
           "Be written inside a catch block."],
          "Cover all possibilities (or have default) so it always yields a value.",
          "The compiler checks exhaustiveness for expressions."),
        q("java-switch-q3",
          "When is if/else still better than switch?",
          ["Never.",
           "When the condition is a range or a compound boolean, not a discrete label.",
           "When there are more than two branches.",
           "When you need to print."],
          "When the condition is a range or a compound boolean, not a discrete label.",
          "switch shines for enums, strings, and small integer menus."),
        q("java-switch-q4",
          "Should this curriculum require pattern-matching switch for DSA?",
          ["Yes, heaps need it.",
           "No: it is a modern language feature, not a DSA gate.",
           "Yes, graphs need it.",
           "Yes, because Helsinki requires it."],
          "No: it is a modern language feature, not a DSA gate.",
          "Pattern matching can wait; if/switch/loops are enough for DSA."),
    ],
    exercises=[
        ex("java-switch-ex1", "Menu with switch expressions",
           "Build a text menu: 1=list, 2=add, 3=quit. Use a switch expression to map the int to an enum or String command. "
           "Handle invalid numbers with default. Compare in comments to an if/else version: which is clearer here? "
           "Target a JDK that supports switch expressions (any current JDK)."),
    ],
)

_add(
    "java-loops",
    hours=1.0,
    objective="Choose for, while, and do-while; write validation loops and controlled iteration.",
    explanation=(
        "while tests before the body; do-while tests after (body runs at least once); for combines init/test/update. "
        "Enhanced for comes with arrays/collections. Helsinki repeating + more-loops is the exercise battery. "
        "Pattern printing is fine as motor practice; prefer problems with a stopping condition you can state in words."
    ),
    mastery=[
        "Implement while and for for the same task and explain the tradeoff.",
        "Write a validation loop that only exits on good input.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-loops-primary", "Helsinki Part 2 — Repeating", H_P2_REPEAT, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " while/repetition exercises."),
        r("java-loops-reference", "Control flow statements", DJ_FLOW, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Looping statements in modern Java."),
        r("java-loops-practice", "Helsinki Part 2 — More loops", H_P2_LOOPS, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 2,
          HELSINKI_NOTE + " Additional loop patterns. Do not copy every exercise; pick representative ones and complete them locally."),
    ],
    questions=[
        q("java-loops-q1",
          "When is do-while the most natural fit?",
          ["When the body must not run if the condition is already false.",
           "When you must run the body once before testing (e.g. show a menu then ask).",
           "When iterating an array by index.",
           "When you need infinite parallelism."],
          "When you must run the body once before testing (e.g. show a menu then ask).",
          "Menus and 'ask until valid' often start with an attempt.",
          mastery=True),
        q("java-loops-q2",
          "for (int i = 0; i < n; i++) vs while:",
          ["for is illegal when n is a variable.",
           "for is convenient when a counter and update belong together; while emphasizes a condition.",
           "while cannot count.",
           "They compile to unrelated bytecode with different results."],
          "for is convenient when a counter and update belong together; while emphasizes a condition.",
          "Same power; choose the one that matches the story of the loop."),
        q("java-loops-q3",
          "An infinite loop `while (true)` is:",
          ["Always a bug.",
           "Acceptable if there is a clear internal exit (return/break) you can justify.",
           "Required for all CLIs.",
           "How Java does garbage collection."],
          "Acceptable if there is a clear internal exit (return/break) you can justify.",
          "Still prefer a named condition when it reads better."),
        q("java-loops-q4",
          "Off-by-one in `for (i = 0; i <= n; i++)` on an array of length n typically:",
          ["Skips index 0.", "Touches a valid extra index n and throws or is a logic error.",
           "Is required in Java.", "Sorts the array."],
          "Touches a valid extra index n and throws or is a logic error.",
          "Valid indices are 0..n-1. `i < n` is the usual bound."),
        q("java-loops-q5",
          "Nested loops for a 2D grid have time that scales with:",
          ["rows + cols always.", "rows * cols for a full traversal.",
           "always O(1).", "the JVM vendor."],
          "rows * cols for a full traversal.",
          "Language loops, not DSA yet — but complexity language starts here."),
    ],
    exercises=[
        ex("java-loops-ex1", "Validation, analysis, pattern",
           "1) Validation loop: read positive integers until the user enters 0; print count, min, max, and sum. Reject non-integers. "
           "2) Print a right triangle of height 5 using nested loops. "
           "3) Rewrite the validation loop as a for-loop if it fits; if not, comment why while is better. "
           + HELSINKI_NOTE,
           difficulty="intermediate"),
    ],
)

_add(
    "java-break-continue",
    hours=0.4,
    objective="Use break and continue deliberately; avoid using them to hide messy structure.",
    explanation=(
        "break leaves the innermost loop or switch. continue skips the rest of this iteration. "
        "Labeled break exists but is rarely the clearest design. Prefer a boolean condition when it reads better."
    ),
    mastery=[
        "Predict break vs continue on a small loop.",
        "Rewrite one continue-loop as a filtered condition.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-break-continue-primary", "Control flow statements", DJ_FLOW, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Branching statements including break and continue."),
        r("java-break-continue-practice", "Helsinki Part 2 — More loops", H_P2_LOOPS, "University of Helsinki",
          "PRACTICE", "interactive_tutorial", 1,
          HELSINKI_NOTE + " Loop control practice."),
    ],
    questions=[
        q("java-break-continue-q1",
          "In `for (int x : nums) { if (x < 0) continue; sum += x; }` continue does what?",
          ["Exits the method.", "Skips negatives, still processes later elements.",
           "Deletes x from the array.", "Restarts the JVM."],
          "Skips negatives, still processes later elements.",
          "Equivalent to wrapping the add in `if (x >= 0)`.",
          mastery=True),
        q("java-break-continue-q2",
          "break inside a nested loop (unlabeled) exits:",
          ["All loops in the method.", "Only the innermost loop.",
           "The program.", "The outer loop only."],
          "Only the innermost loop.",
          "Labeled break can exit outer loops; prefer extracting a method."),
        q("java-break-continue-q3",
          "A loop that is mostly continue-guards may be clearer as:",
          ["More labels.", "if-conditions that only run the real work on interesting cases.",
           "A switch on Thread.", "catching Error."],
          "if-conditions that only run the real work on interesting cases.",
          "continue is fine; it is not a badge of cleverness."),
        q("java-break-continue-q4",
          "break in switch vs loop:",
          ["The keyword is illegal in loops.",
           "Same keyword, different enclosing structure: ends the switch or the loop.",
           "break in a loop compiles only on Friday.",
           "continue works in switch the same as break."],
          "Same keyword, different enclosing structure: ends the switch or the loop.",
          "Arrow switch cases do not need break."),
    ],
    exercises=[
        ex("java-break-continue-ex1", "Search then skip",
           "Given a hardcoded int array, print the first even number (use break) then in a second loop print all odd numbers (use continue to skip evens). "
           "Rewrite the second loop without continue. Which version do you prefer and why?"),
    ],
)

_add(
    "java-method-basics",
    hours=1.25,
    objective="Declare methods with parameters and return values; explain Java pass-by-value; refactor a monolithic main.",
    explanation=(
        "A method has a name, parameter list, return type (or void), and body. Callers pass arguments. "
        "Java is pass-by-value: primitives are copied; for objects, the reference value is copied, so the callee can mutate the same object "
        "but cannot make the caller's variable point elsewhere. "
        + DSA_METHODS
    ),
    mastery=[
        "Write methods with parameters and return values independently.",
        "Explain Java parameter passing (pass-by-value, including of references).",
        "Refactor a monolithic program into methods.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-method-basics-primary", "Helsinki Part 2 — Methods", H_P2_METHODS, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Method exercises. This is the DSA methods gate."),
        r("java-method-basics-reference", "Defining methods", DJ_METH, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Method declarations in classes."),
        r("java-method-basics-deep", "Calling methods and constructors", DJ_CALL, "Dev.java",
          "DEEP_DIVE", "documentation", 2,
          "Passing information into methods. Combine with the pass-by-value lesson; Java is not pass-by-reference."),
    ],
    questions=[
        q("java-method-basics-q1",
          "void vs a return type:",
          ["void methods cannot be named.",
           "void means the method does not return a value to the caller.",
           "void means the method cannot print.",
           "Returning int requires the method to be static."],
          "void means the method does not return a value to the caller.",
          "Use void for actions; return types for computations you will use.",
          mastery=True),
        q("java-method-basics-q2",
          "void bump(int n) { n++; } called as bump(x); — x in the caller:",
          ["Always increases.",
           "Is unchanged; n is a copy of the primitive value.",
           "Becomes null.",
           "Does not compile."],
          "Is unchanged; n is a copy of the primitive value.",
          "Pass-by-value of the int."),
        q("java-method-basics-q3",
          "void append(StringBuilder sb) { sb.append(\"!\"); } — after append(callerSb):",
          ["callerSb is unchanged because Java is pass-by-value.",
           "The same StringBuilder object is mutated; the caller's reference still points at it.",
           "callerSb is reassigned to a new object automatically.",
           "StringBuilder cannot be a parameter."],
          "The same StringBuilder object is mutated; the caller's reference still points at it.",
          "The reference is copied; both copies point at one mutable object. Not pass-by-reference."),
        q("java-method-basics-q4",
          "void rebind(StringBuilder sb) { sb = new StringBuilder(\"z\"); } — caller:",
          ["Now points at \"z\".",
           "Still points at the original object; only the parameter was rebound.",
           "Is set to null.",
           "Throws."],
          "Still points at the original object; only the parameter was rebound.",
          "Rebinding the copy does not rebind the caller's variable."),
        q("java-method-basics-q5",
          "Why split a 80-line main into methods before DSA?",
          ["The JVM requires fewer than 20 lines in main.",
           "You need named operations you can test, reuse, and later put on arrays/lists.",
           "Helsinki forbids main after part 2.",
           "Methods make programs slower, which trains complexity."],
          "You need named operations you can test, reuse, and later put on arrays/lists.",
          "Decomposition is the skill DSA solutions need."),
        q("java-method-basics-q6",
          "A first recursion (factorial/sum) is introduced here as:",
          ["Required for all later DSA.",
           "A method that calls itself with a smaller argument and a base case.",
           "The only way to write a loop in Java.",
           "Undefined in Java."],
          "A method that calls itself with a smaller argument and a base case.",
          "Loops remain the default. Recursion returns in DSA with trees."),
        q("java-method-basics-q7",
          "static methods on a simple exercise class are used because:",
          ["They are faster than instances always.",
           "You can call them from main without constructing an object.",
           "Non-static methods are deprecated.",
           "DSA forbids objects."],
          "You can call them from main without constructing an object.",
          "Instance methods become natural once you have classes."),
    ],
    exercises=[
        ex("java-method-basics-ex1", "Refactor the CLI into methods",
           "Take a monolithic program (your calculator or a copy-paste 40-line main). Extract: parseIntSafe, prompt, add, subtract, and a runLoop. "
           "Add a recursive method `sumTo(int n)` with a base case, plus an iterative equivalent; print both for n=10. "
           "Write a 4-sentence explanation of pass-by-value using one primitive example and one StringBuilder example. "
           + DSA_METHODS,
           difficulty="intermediate"),
    ],
)

_add(
    "java-overloading",
    hours=0.5,
    objective="Overload methods by parameter lists and explain that return type alone is not enough.",
    explanation=(
        "Overloading: same name, different parameter types or arity. The compiler picks the best match. "
        "You cannot overload on return type only. Constructors can overload too (next OOP module). "
        "Do not confuse with overriding (runtime, inheritance)."
    ),
    mastery=[
        "Write two useful overloads of the same name.",
        "Explain why return type cannot be the only difference.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-overloading-primary", "Helsinki Part 5 — Method and constructor overloading", H_P5_OVER, "University of Helsinki",
          "PRIMARY", "interactive_tutorial", 0,
          HELSINKI_NOTE + " Overloading exercises (later in Helsinki than our sequence; use them when you reach this topic)."),
        r("java-overloading-reference", "Defining methods", DJ_METH, "Dev.java",
          "REFERENCE", "documentation", 1,
          "Method declarations; combine with the overloading lesson."),
    ],
    questions=[
        q("java-overloading-q1",
          "Which pair is a valid overload of format?",
          ["format(int x) and format(int y) — different parameter names.",
           "format(int x) and format(String s).",
           "int format() and String format() with no parameters.",
           "format() in two classes with the same parameter list, called overload."],
          "format(int x) and format(String s).",
          "The signature is name plus parameter types, not names or return type alone.",
          mastery=True),
        q("java-overloading-q2",
          "Overload resolution happens:",
          ["At runtime based on the object's class only.",
           "At compile time based on the static types of arguments.",
           "Randomly.",
           "Only if methods are synchronized."],
          "At compile time based on the static types of arguments.",
          "Overriding is the runtime dispatch story."),
        q("java-overloading-q3",
          "max(int,int) and max(double,double): max(2, 3.5) typically:",
          ["Does not compile.",
           "Picks a widening match to the double overload if that is the best fit.",
           "Always uses int and truncates 3.5.",
           "Calls both."],
          "Picks a widening match to the double overload if that is the best fit.",
          "If both could match equally, you get an ambiguity error — fix with a cast."),
        q("java-overloading-q4",
          "Why overload instead of printInt/printDouble?",
          ["The JVM requires one name per class.",
           "One concept, several type shapes — easier to read at the call site.",
           "Overloading is faster than one method.",
           "Helsinki forbids two names."],
          "One concept, several type shapes — easier to read at the call site.",
          "Don't overload unrelated behaviors onto one name."),
    ],
    exercises=[
        ex("java-overloading-ex1", "Area overloads",
           "Write area(int side) for a square, area(int w, int h) for a rectangle, and area(double radius) for a circle. "
           "Call all three from main. Attempt a fourth overload that differs only by return type; record the compiler error in a comment."),
    ],
)

_add(
    "java-scope",
    hours=0.5,
    objective="Reason about local vs parameter vs class-level variables and shadowing.",
    explanation=(
        "A local variable lives from its declaration to the end of its block. Parameters are locals. "
        "Fields (later) live as long as the object. Nested blocks can shadow. Loops' for-init variables are scoped to the loop."
    ),
    mastery=[
        "Identify which variables are in scope at a given line.",
        "Fix a shadowing bug.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("java-scope-primary", "Creating variables and naming them", DJ_VAR, "Dev.java",
          "PRIMARY", "documentation", 0,
          "Variable naming and declaration; combine with block scope in this lesson."),
        r("java-scope-reference", "Helsinki Part 2 — Methods", H_P2_METHODS, "University of Helsinki",
          "REFERENCE", "interactive_tutorial", 1,
          HELSINKI_NOTE + " Methods make scope mistakes obvious (variables not visible across methods)."),
    ],
    questions=[
        q("java-scope-q1",
          "A variable declared inside an if block is visible:",
          ["In the whole method.", "Only inside that block (and nested blocks).",
           "In other methods of the class automatically.", "After the method returns."],
          "Only inside that block (and nested blocks).",
          "Block scope.",
          mastery=True),
        q("java-scope-q2",
          "Two methods each have a local named count. They:",
           ["Share one variable.", "Are independent; each call has its own count.",
            "Do not compile.", "Must be synchronized."],
          "Are independent; each call has its own count.",
          "Each invocation has its own stack frame."),
        q("java-scope-q3",
          "for (int i = 0; i < n; i++) { } then using i after the loop:",
          ["i is n.", "Typically a compile error; i is out of scope.",
           "i is 0.", "i is n-1."],
          "Typically a compile error; i is out of scope.",
          "Declare i before the for if you need it afterward."),
        q("java-scope-q4",
          "A parameter named size and a local named size in the same method:",
          ["Is required.", "The local shadows the parameter for the rest of the block — usually a mistake.",
           "Merges them into an array.", "Promotes both to fields."],
          "The local shadows the parameter for the rest of the block — usually a mistake.",
          "Pick different names."),
    ],
    exercises=[
        ex("java-scope-ex1", "Scope hunt",
           "Write a method with an if-block local, a loop index, and a parameter. Deliberately try to print the if-local after the block; paste the compiler error into a comment. "
           "Then write a correct version that returns all needed values. Explain in three sentences where each variable lives."),
    ],
)
