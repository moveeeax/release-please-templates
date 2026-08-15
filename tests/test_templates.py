"""Every shipped template must be a valid release-please setup, and the sample
commits under examples/ must produce the version bump we claim."""
import json
import os
import glob

import pytest

from rpt import validate_config, validate_manifest, parse_commits, simulate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = sorted(glob.glob(os.path.join(ROOT, "templates", "*")))


def _load(path):
    with open(path) as f:
        return json.load(f)


@pytest.mark.parametrize("tpl", TEMPLATES, ids=[os.path.basename(t) for t in TEMPLATES])
def test_template_config_and_manifest_valid(tpl):
    config = _load(os.path.join(tpl, "release-please-config.json"))
    manifest = _load(os.path.join(tpl, ".release-please-manifest.json"))
    errs = validate_config(config) + validate_manifest(config, manifest)
    assert errs == [], errs


@pytest.mark.parametrize("tpl", TEMPLATES, ids=[os.path.basename(t) for t in TEMPLATES])
def test_template_ships_workflow(tpl):
    wf = os.path.join(tpl, ".github", "workflows", "release-please.yml")
    assert os.path.exists(wf)
    body = open(wf).read()
    assert "googleapis/release-please-action@v4" in body
    assert "config-file:" in body and "manifest-file:" in body


def test_monorepo_manifest_demo():
    demo = os.path.join(ROOT, "examples", "monorepo-manifest-demo")
    config = _load(os.path.join(demo, "release-please-config.json"))
    manifest = _load(os.path.join(demo, ".release-please-manifest.json"))
    assert validate_config(config) + validate_manifest(config, manifest) == []
    expected = _load(os.path.join(demo, "expected.json"))
    for path, spec in expected.items():
        commits = parse_commits(spec["commits"])
        r = simulate(config, manifest[path], commits)
        assert r["next_version"] == spec["next_version"], (path, r["next_version"])
