import pytest

from rpt import (
    parse_commits, release_level, next_version, changelog, simulate,
    LEVEL_NONE, LEVEL_PATCH, LEVEL_MINOR, LEVEL_MAJOR,
)
from rpt.bump import render_changelog, parse_version


def test_level_precedence():
    cs = parse_commits("fix: a\nfeat: b")
    assert release_level(cs) == LEVEL_MINOR
    cs = parse_commits("feat: b\nfix!: c")
    assert release_level(cs) == LEVEL_MAJOR
    cs = parse_commits("chore: x\ndocs: y")
    assert release_level(cs) == LEVEL_NONE


def test_next_version_post_1_0():
    assert next_version("1.4.2", LEVEL_PATCH) == "1.4.3"
    assert next_version("1.4.2", LEVEL_MINOR) == "1.5.0"
    assert next_version("1.4.2", LEVEL_MAJOR) == "2.0.0"
    assert next_version("1.4.2", LEVEL_NONE) is None


def test_pre_1_0_options():
    opts = {"bump-minor-pre-major": True, "bump-patch-for-minor-pre-major": True}
    # breaking -> minor while 0.x
    assert next_version("0.3.0", LEVEL_MAJOR, opts) == "0.4.0"
    # feat -> patch while 0.x
    assert next_version("0.3.0", LEVEL_MINOR, opts) == "0.3.1"
    # fix -> patch as usual
    assert next_version("0.3.0", LEVEL_PATCH, opts) == "0.3.1"
    # without the options, normal semver
    assert next_version("0.3.0", LEVEL_MAJOR) == "1.0.0"


def test_changelog_groups_by_type_and_order():
    sections = [
        {"type": "feat", "section": "Features"},
        {"type": "fix", "section": "Bug Fixes"},
        {"type": "chore", "section": "Misc", "hidden": True},
    ]
    cs = parse_commits("chore: bump deps\nfix: b\nfeat: a\nfix: c")
    groups = changelog(cs, sections)
    # hidden chore is dropped; Features before Bug Fixes; both fixes grouped
    assert [g["section"] for g in groups] == ["Features", "Bug Fixes"]
    assert [c.subject for c in groups[1]["commits"]] == ["b", "c"]


def test_simulate_end_to_end():
    config = {
        "release-type": "go",
        "bump-minor-pre-major": True,
        "changelog-sections": [
            {"type": "feat", "section": "Features"},
            {"type": "fix", "section": "Bug Fixes"},
        ],
    }
    cs = parse_commits("feat: add flag\nfix: nil deref")
    r = simulate(config, "1.0.0", cs)
    assert r["release"] is True
    assert r["next_version"] == "1.1.0"
    assert "## 1.1.0" in r["changelog_md"]
    assert "### Features" in r["changelog_md"]


def test_simulate_no_release():
    config = {"release-type": "go"}
    cs = parse_commits("docs: readme\nchore: tidy")
    r = simulate(config, "1.0.0", cs)
    assert r["release"] is False
    assert r["next_version"] is None


def test_render_breaking_section():
    cs = parse_commits("feat!: new api")
    md = render_changelog("2.0.0", changelog(cs, [{"type": "feat", "section": "Features"}]), breaking=cs)
    assert "BREAKING CHANGES" in md


def test_parse_version_rejects_junk():
    with pytest.raises(ValueError):
        parse_version("nope")
