"""Domain 0 topic payloads keyed by slug. Prerequisites/next_topic are not stored here."""

from __future__ import annotations

from _d0_helpers import (
    CS50_N0,
    CS50_N1,
    CS50_W0,
    CS50_W1,
    MIT_CLI,
    MIT_DBG,
    MIT_DEV,
    MIT_GIT,
    MIT_QUALITY,
    MIT_SHELL,
    MIT_SHIP,
    WSL,
    ex,
    q,
    r,
)


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


CONTENT = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


_add(
    "cf-bits-and-bytes",
    hours=0.5,
    objective="Explain how information is measured in bits and bytes.",
    explanation=(
        "A bit is a binary digit: 0 or 1. A byte is eight bits and can represent 256 distinct patterns. "
        "Text, images, and instructions are all stored as bits; the meaning comes from the encoding we agree on. "
        "CS50 Week 0 is the selected source for this representation idea. Do not complete the whole CS50 course."
    ),
    mastery=[
        "Explain bits vs bytes without notes.",
        "Convert a small quantity between bits and bytes.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        r("cf-bits-and-bytes-primary", "CS50x 2026 Week 0 (representation)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Use the unary/binary/decimal and representation sections only. Not the full Scratch project."),
        r("cf-bits-and-bytes-reference", "CS50x 2026 Lecture 0 notes", CS50_N0, "CS50x", "REFERENCE", "documentation", 1,
          "Notes on bits, bytes, ASCII, and abstraction."),
    ],
    questions=[
        q("cf-bits-and-bytes-q1", "Why can one sequence of bits represent a number, a letter, or a color?",
          ["Hardware stores a different physical type for each kind of data.",
           "The same bit patterns are interpreted using an agreed encoding.",
           "Bytes can only represent numbers; letters use a separate chip.",
           "Unicode replaces bits with characters at the hardware level."],
          "The same bit patterns are interpreted using an agreed encoding.",
          "Bits are just on/off. ASCII, Unicode, and RGB assign meaning to patterns.", "medium", True),
        q("cf-bits-and-bytes-q2", "How many distinct values can one byte represent?",
          ["8", "16", "256", "1024"], "256",
          "Eight bits give 2^8 = 256 patterns (0 through 255).", "easy", True),
        q("cf-bits-and-bytes-q3", "If a file is 4 KiB, about how many bits is that?",
          ["32 bits", "4096 bits", "32768 bits", "4 million bits"], "32768 bits",
          "4 KiB is 4096 bytes; 4096 × 8 = 32768 bits.", "medium"),
        q("cf-bits-and-bytes-q4", "What is the most accurate description of a bit?",
          ["A decimal digit from 0–9", "The smallest unit of digital information, 0 or 1",
           "Always equal to one character of text", "A measure of processor speed"],
          "The smallest unit of digital information, 0 or 1",
          "Character encodings use multiple bits per character.", "easy"),
    ],
    exercises=[
        ex("cf-bits-and-bytes-ex1", "Bits vs bytes conversions",
           "Convert 3 bytes to bits, 40 bits to bytes (state if it divides evenly), and 2 KiB to bytes. "
           "Write one sentence on why file sizes are usually quoted in bytes or kibibytes rather than raw bits."),
    ],
)

_add(
    "cf-binary",
    hours=0.75,
    objective="Read and convert small binary values.",
    explanation=(
        "Binary is base-2. Each place is a power of two. CS50 Week 0 covers unary, binary, and decimal. "
        "Practice converting values up to 8 bits by hand so the idea is automatic."
    ),
    mastery=[
        "Explain positional representation in base 2.",
        "Convert between binary and decimal for values up to 8 bits without copying.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-binary-primary", "CS50x 2026 Week 0 (binary/decimal)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Unary/binary/decimal sections only."),
        r("cf-binary-reference", "CS50x 2026 Lecture 0 notes (binary)", CS50_N0, "CS50x", "REFERENCE", "documentation", 1,
          "Worked binary examples in the official notes."),
    ],
    questions=[
        q("cf-binary-q1", "What decimal value is binary 00001101?",
          ["11", "12", "13", "15"], "13",
          "8+4+1 = 13.", "easy", True),
        q("cf-binary-q2", "Why do computers use binary rather than decimal internally?",
          ["Decimal arithmetic is illegal in hardware.",
           "Two stable physical states (on/off) are reliable to implement.",
           "Binary uses fewer digits than decimal for every number.",
           "Humans cannot understand decimal."],
          "Two stable physical states (on/off) are reliable to implement.",
          "Electronics distinguish two levels more reliably than ten.", "medium", True),
        q("cf-binary-q3", "What happens when you add 1 to an 8-bit value that is already 11111111?",
          ["It becomes 256 stored in the same 8 bits.",
           "It wraps to 00000000 if treated as an 8-bit unsigned value.",
           "The CPU refuses to add.",
           "It becomes 11111110."],
          "It wraps to 00000000 if treated as an 8-bit unsigned value.",
          "Fixed-width unsigned overflow wraps. CS50 Week 1 later names this integer overflow.", "hard"),
        q("cf-binary-q4", "Which place values do you add for binary 1010?",
          ["8+2", "8+4", "4+2+1", "16+2"], "8+2",
          "1010 is 8 + 0 + 2 + 0 = 10.", "easy"),
    ],
    exercises=[
        ex("cf-binary-ex1", "Five conversions",
           "Convert these binary values to decimal: 00000010, 00010100, 00111111, 10000000, 11110000. "
           "Then convert decimal 19 and 40 to 8-bit binary. Write how you checked one answer (powers of two)."),
    ],
)

_add(
    "cf-hexadecimal",
    hours=0.5,
    objective="Use hexadecimal as a compact view of binary.",
    explanation=(
        "Hexadecimal is base-16. Each hex digit is exactly four bits, so 1111 is F and a byte is two hex digits. "
        "CS50 Week 0 teaches binary/decimal; hex is the same positional idea with grouping. "
        "You will see hex in memory dumps, color codes (#RRGGBB), and addresses."
    ),
    mastery=[
        "Explain why hex is a convenient notation for binary.",
        "Convert between binary, hex, and decimal for small values.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-hexadecimal-primary", "CS50x 2026 Week 0 (positional representation)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Use binary/decimal as the foundation; apply the same positional idea to base-16. RGB on this page is hex in disguise."),
        r("cf-hexadecimal-reference", "CS50x 2026 Lecture 0 notes (RGB/bytes)", CS50_N0, "CS50x", "REFERENCE", "documentation", 1,
          "RGB uses byte values commonly written in hex in CSS and tools."),
    ],
    questions=[
        q("cf-hexadecimal-q1", "Why is one hex digit equal to four bits?",
          ["Hex is base 10 and 10 is near 8.",
           "16 = 2^4, so four bits have 16 patterns, one per hex digit.",
           "ASCII maps letters A–F to four bits each.",
           "CPUs can only add in hex."],
          "16 = 2^4, so four bits have 16 patterns, one per hex digit.",
          "Nibble = 4 bits = one hex digit.", "medium", True),
        q("cf-hexadecimal-q2", "What is binary 11110000 in hex?",
          ["F0", "0F", "E0", "FF"], "F0",
          "1111 is F and 0000 is 0.", "easy", True),
        q("cf-hexadecimal-q3", "A CSS color #00FF00 uses which idea from CS50 Week 0?",
          ["Threads in Scratch",
           "RGB: three bytes of color, often written in hex",
           "Pseudocode keywords",
           "Floating-point imprecision"],
          "RGB: three bytes of color, often written in hex",
          "Week 0 introduces RGB; hex is the usual written form.", "medium"),
        q("cf-hexadecimal-q4", "Which conversion is correct?",
          ["0x2A is decimal 32", "0x10 is decimal 10", "0x10 is decimal 16", "0xFF is decimal 128"],
          "0x10 is decimal 16",
          "Hex 10 is 1×16 + 0 = 16.", "easy"),
    ],
    exercises=[
        ex("cf-hexadecimal-ex1", "Nibble grouping",
           "Convert binary 11010111 to hex by splitting into two 4-bit groups. Convert hex 3C to binary and to decimal. "
           "Explain in one sentence why programmers prefer hex over long binary strings."),
    ],
)
