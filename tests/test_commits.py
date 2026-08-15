from rpt import parse_commit, parse_commits


def test_basic_header():
    c = parse_commit("feat: add retry flag")
    assert c.type == "feat"
    assert c.subject == "add retry flag"
    assert c.scope is None
    assert not c.breaking


def test_scope_and_bang():
    c = parse_commit("feat(api)!: drop v1 endpoint")
    assert c.type == "feat"
    assert c.scope == "api"
    assert c.breaking is True
    assert c.scoped == "feat(api)"


def test_breaking_footer():
    msg = "fix: correct paging\n\nBREAKING CHANGE: page index is now 1-based"
    c = parse_commit(msg)
    assert c.type == "fix"
    assert c.breaking is True


def test_non_conventional_is_none():
    assert parse_commit("update stuff") is None
    assert parse_commit("") is None


def test_parse_many_drops_junk():
    text = "feat: a\nnot a commit\nfix: b\n\n"
    cs = parse_commits(text)
    assert [c.type for c in cs] == ["feat", "fix"]
