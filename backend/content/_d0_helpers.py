"""Helpers for Domain 0 content authoring. No invented URLs."""

from __future__ import annotations

WSL = (
    "Windows: complete this in WSL (Ubuntu) or a Linux VM. "
    "Do not use PowerShell or cmd.exe as a substitute for the Unix-shell curriculum."
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
    assert answer in options
    assert len(options) == 4
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


CS50_W0 = "https://cs50.harvard.edu/x/weeks/0/"
CS50_W1 = "https://cs50.harvard.edu/x/weeks/1/"
CS50_N0 = "https://cs50.harvard.edu/x/notes/0/"
CS50_N1 = "https://cs50.harvard.edu/x/notes/1/"
MIT_SHELL = "https://missing.csail.mit.edu/2026/course-shell/"
MIT_CLI = "https://missing.csail.mit.edu/2026/command-line-environment/"
MIT_DEV = "https://missing.csail.mit.edu/2026/development-environment/"
MIT_DBG = "https://missing.csail.mit.edu/2026/debugging-profiling/"
MIT_GIT = "https://missing.csail.mit.edu/2026/version-control/"
MIT_SHIP = "https://missing.csail.mit.edu/2026/shipping-code/"
MIT_QUALITY = "https://missing.csail.mit.edu/2026/code-quality/"
