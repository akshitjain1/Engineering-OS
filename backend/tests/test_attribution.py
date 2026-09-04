"""The running app must say whose work it is.

None of this stops anyone. A person holding the source can delete every line of
it in a minute, and no amount of cleverness changes that -- there is no
technical mechanism that survives someone with the code and a motive.

What it does is make the claim travel with the software. A deployed copy names
its author in its API, its headers and its own interface, so removing the
attribution has to be a deliberate act rather than an oversight -- and under
AGPL section 5 a deliberate act is a licence violation.

These tests exist so that a refactor cannot quietly drop it.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUTHOR = "Akshit Jain"


def test_health_states_the_author_and_licence(client):
    body = client.get("/api/health").json()

    assert body["author"] == AUTHOR
    assert body["license"] == "AGPL-3.0-or-later"
    assert "github.com/akshitjain1" in body["source"]
    assert AUTHOR in body["copyright"]


def test_every_response_carries_the_attribution_headers(client):
    for path in ("/api/health", "/api/curriculum/tree"):
        headers = client.get(path).headers
        assert headers.get("X-Engineering-OS-Author") == AUTHOR, path
        assert headers.get("X-Engineering-OS-License") == "AGPL-3.0-or-later", path
        assert "github.com/akshitjain1" in headers.get("X-Engineering-OS-Source", ""), path


def test_the_openapi_document_names_the_author(client):
    spec = client.get("/openapi.json").json()

    assert spec["info"]["contact"]["name"] == AUTHOR
    assert spec["info"]["license"]["name"] == "AGPL-3.0-or-later"
    assert AUTHOR in spec["info"]["description"]


def test_the_licence_is_the_real_agpl():
    """A licence file that is not the licence protects nothing."""
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in text
    assert "Version 3, 19 November 2007" in text
    # Section 13 is the reason AGPL was chosen over GPL: it reaches hosted copies.
    assert "Remote Network Interaction" in text
    assert len(text) > 30_000, "the licence text looks truncated"


def test_the_notice_names_the_author_and_the_origin():
    text = (ROOT / "NOTICE").read_text(encoding="utf-8")

    assert f"Copyright (C) 2026 {AUTHOR}" in text
    assert "github.com/akshitjain1/Engineering-OS" in text
    assert "22 August 2026" in text


def test_the_readme_carries_the_copyright_line():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert AUTHOR in text.split("\n", 4)[2], "the copyright line left the top of the README"
    assert "AGPL" in text


def test_third_party_material_is_credited_rather_than_claimed():
    """The linked sources belong to their publishers. Saying so is the honest
    half of claiming the rest."""
    text = (ROOT / "NOTICE").read_text(encoding="utf-8")

    assert "THIRD-PARTY MATERIAL" in text
    for name in ("GeeksforGeeks", "LeetCode", "MIT OpenCourseWare"):
        assert name in text
