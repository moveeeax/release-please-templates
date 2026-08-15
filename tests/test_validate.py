from rpt import validate_config, validate_manifest


def test_valid_single_package():
    config = {"release-type": "go", "packages": {".": {}}}
    assert validate_config(config) == []


def test_missing_release_type():
    config = {"packages": {".": {}}}
    errs = validate_config(config)
    assert any("missing release-type" in e for e in errs)


def test_unknown_release_type():
    config = {"packages": {".": {"release-type": "cobol"}}}
    errs = validate_config(config)
    assert any("unknown release-type" in e for e in errs)


def test_multipackage_requires_components():
    config = {"packages": {"a": {"release-type": "go"}, "b": {"release-type": "go"}}}
    errs = validate_config(config)
    assert any("needs a 'component'" in e for e in errs)


def test_multipackage_duplicate_components():
    config = {"packages": {
        "a": {"release-type": "go", "component": "x"},
        "b": {"release-type": "go", "component": "x"},
    }}
    errs = validate_config(config)
    assert any("duplicate 'component'" in e for e in errs)


def test_manifest_must_cover_packages():
    config = {"packages": {"a": {"release-type": "go", "component": "a"},
                            "b": {"release-type": "go", "component": "b"}}}
    manifest = {"a": "1.0.0"}
    errs = validate_manifest(config, manifest)
    assert any("manifest missing version for package 'b'" in e for e in errs)


def test_manifest_semver_and_orphans():
    config = {"packages": {"a": {"release-type": "go"}}}
    errs = validate_manifest(config, {"a": "bad", "z": "1.0.0"})
    assert any("not a semver" in e for e in errs)
    assert any("not present in config.packages" in e for e in errs)
