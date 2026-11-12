import io
import json
import urllib.request

import pytest

from rpt import SchemaLoadError, load_schema, validate_config, validate_schema
from rpt.cli import main


def _go(**extra):
    config = {"release-type": "go", "packages": {".": {}}}
    config.update(extra)
    return config


def test_vendored_schema_loads():
    schema = load_schema()
    assert schema["title"] == "release-please manifest config schema"
    assert "ReleaserConfigOptions" in schema["definitions"]


def test_minimal_config_passes_schema():
    assert validate_schema(_go()) == []


def test_top_level_typo_gets_hint():
    config = _go(**{"bump-minor-pre-majr": True})
    errs = validate_config(config)
    assert errs == [
        "config: unknown key 'bump-minor-pre-majr' (did you mean 'bump-minor-pre-major'?)"
    ]


def test_unknown_key_without_close_match_has_no_hint():
    errs = validate_schema(_go(zzz=1))
    assert errs == ["config: unknown key 'zzz'"]


def test_package_typo_gets_hint():
    config = {"packages": {"a": {"release-type": "go", "componnet": "a"}}}
    errs = validate_schema(config)
    assert errs == ["config['packages']['a']: unknown key 'componnet' (did you mean 'component'?)"]


def test_package_only_keys_are_allowed():
    config = {"packages": {"a": {
        "release-type": "go", "component": "a", "package-name": "a",
        "changelog-path": "CHANGES.md", "label": "x", "release-label": "y",
    }}}
    assert validate_schema(config) == []


def test_wrong_option_type():
    errs = validate_schema(_go(**{"include-v-in-tag": "yes"}))
    assert errs == ["config['include-v-in-tag']: 'yes' is not of type 'boolean'"]


def test_extra_files_entries():
    config = _go(**{"extra-files": [
        "version.txt",
        {"type": "json", "path": "package.json", "jsonpath": "$.version"},
        {"type": "json", "path": "app.json"},
        {"type": "xml", "path": "a.xml", "jsonpath": "$.v"},
        5,
    ]})
    errs = validate_schema(config)
    assert errs == [
        "config['extra-files'][2]: 'jsonpath' is a required property",
        "config['extra-files'][3]: 'xpath' is a required property",
        "config['extra-files'][4]: 5 is not of type 'string'",
    ]


def test_changelog_section_reported_once():
    errs = validate_config(_go(**{"changelog-sections": [{"type": "feat"}]}))
    assert errs == ["config['changelog-sections'][0]: 'section' is a required property"]


def test_non_object_config():
    assert validate_config([1]) == ["config: [1] is not of type 'object'"]


def test_custom_schema_dict():
    schema = {"type": "object", "required": ["packages"]}
    errs = validate_config({"release-type": "go"}, schema)
    assert "config: 'packages' is a required property" in errs
    # the hand-written changelog check still runs when the schema lacks it
    errs = validate_config(_go(**{"changelog-sections": [{"type": "feat"}]}), schema)
    assert errs == ["changelog-sections[0]: needs both 'type' and 'section'"]


def test_load_schema_from_path_and_file_url(tmp_path):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps({"type": "object", "title": "local"}))
    assert load_schema(str(p))["title"] == "local"
    assert load_schema(p.as_uri())["title"] == "local"


def test_load_schema_from_http(monkeypatch):
    seen = {}

    def fake_urlopen(url, timeout):
        seen["url"], seen["timeout"] = url, timeout
        return io.BytesIO(b'{"title": "remote"}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert load_schema("https://example.test/config.json")["title"] == "remote"
    assert seen == {"url": "https://example.test/config.json", "timeout": 10}


@pytest.mark.parametrize("content", ["not json", "[1, 2]"])
def test_load_schema_bad_content(tmp_path, content):
    p = tmp_path / "schema.json"
    p.write_text(content)
    with pytest.raises(SchemaLoadError):
        load_schema(str(p))


def test_load_schema_missing_file(tmp_path):
    with pytest.raises(SchemaLoadError):
        load_schema(str(tmp_path / "nope.json"))


def _write(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def test_cli_reports_typo(tmp_path, capsys):
    cfg = _write(tmp_path, "c.json", _go(**{"bump-minor-pre-majr": True}))
    assert main(["validate", cfg]) == 1
    err = capsys.readouterr().err
    assert "did you mean 'bump-minor-pre-major'?" in err


def test_cli_schema_url_override(tmp_path, capsys):
    cfg = _write(tmp_path, "c.json", _go(**{"custom-key": 1}))
    assert main(["validate", cfg]) == 1
    capsys.readouterr()
    schema = _write(tmp_path, "s.json", {"type": "object"})
    assert main(["validate", cfg, "--schema-url", schema]) == 0
    assert "ok:" in capsys.readouterr().out


def test_cli_unloadable_schema(tmp_path, capsys):
    cfg = _write(tmp_path, "c.json", _go())
    assert main(["validate", cfg, "--schema-url", str(tmp_path / "missing.json")]) == 2
    assert "cannot load schema" in capsys.readouterr().err
