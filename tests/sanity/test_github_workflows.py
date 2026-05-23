# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep for .github/workflows/*.yml. The CI pipeline is the
# load-bearing thing that gates every Galaxy release; a workflow YAML
# typo silently disables a check. Pin the basics here.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


def _workflow_files():
    if not WORKFLOWS_DIR.exists():
        return []
    return sorted(p for p in WORKFLOWS_DIR.glob("*.yml") if p.is_file())


WORKFLOWS = _workflow_files()


def test_workflows_directory_exists():
    """Without .github/workflows/, the auto-bump pipeline never fires
    and Galaxy releases stop."""
    assert WORKFLOWS_DIR.is_dir(), (
        ".github/workflows/ directory is missing -- no CI runs without it"
    )
    assert WORKFLOWS, "no .yml workflow files found in .github/workflows/"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_yaml_parses(path):
    """Every workflow file must be valid YAML. A parse error is silent
    on the GitHub side -- the workflow just never registers."""
    try:
        parsed = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        pytest.fail(f"{path.name}: YAML parse error: {exc}")
    assert isinstance(parsed, dict), (
        f"{path.name}: top-level must be a dict, got {type(parsed).__name__}"
    )


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_has_name_and_trigger(path):
    """Every workflow must declare `name:` (shows in the runs UI) and
    `on:` (when it fires). GitHub silently accepts a workflow with
    only `jobs:` but it never runs."""
    parsed = yaml.safe_load(path.read_text())
    assert parsed.get("name"), f"{path.name}: missing top-level `name:`"
    # PyYAML parses the unquoted `on:` key as Python boolean True.
    # GitHub Actions accepts both -- the schema is a YAML quirk.
    on_key = parsed.get("on") if "on" in parsed else parsed.get(True)
    assert on_key, f"{path.name}: missing top-level `on:` trigger"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_has_jobs(path):
    """Every workflow must declare at least one job. A no-job workflow
    runs successfully but does nothing -- worst kind of false-green."""
    parsed = yaml.safe_load(path.read_text())
    jobs = parsed.get("jobs")
    assert isinstance(jobs, dict) and jobs, (
        f"{path.name}: missing or empty `jobs:` mapping"
    )


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_jobs_pin_runs_on(path):
    """Each job needs `runs-on:` (or the YAML composes via reusable
    workflow `uses:`). Missing runs-on fails the job at runtime with
    a confusing error."""
    parsed = yaml.safe_load(path.read_text())
    bad = []
    for job_name, job in (parsed.get("jobs") or {}).items():
        if not isinstance(job, dict):
            bad.append(f"{job_name} (not a dict)")
            continue
        if "uses" in job:
            continue  # reusable workflow composition; runs-on comes from there
        if not job.get("runs-on"):
            bad.append(job_name)
    assert not bad, (
        f"{path.name}: jobs missing `runs-on:` (and not using a reusable "
        f"workflow): {bad}"
    )


def test_critical_workflows_present():
    """Pin the workflows the release pipeline depends on. Removing
    any of these silently breaks the auto-publish cycle."""
    expected = {
        "ci.yml",                 # core pytest pyramid
        "release.yml",            # ansible-galaxy publish
        "auto-bump.yml",          # version increment on every push
        "docs-lint.yml",          # antsibull-docs gate
        "ansible-test.yml",       # sanity / yamllint
        "matrix.yml",             # multi-python coverage
        "codeql.yml",             # security
        "integration-live.yml",   # live-gateway smoke
        "mutation-test.yml",      # nightly mutmut
        "docs-publish.yml",       # mkdocs site to GitHub Pages
    }
    present = {p.name for p in WORKFLOWS}
    missing = expected - present
    assert not missing, (
        f"critical workflows missing from .github/workflows/: {missing}"
    )


@pytest.mark.parametrize(
    "wf,max_minutes",
    [
        ("release.yml", 30),          # publish runs in seconds, ceiling generous
        ("auto-bump.yml", 10),        # version bump is fast
        ("ci.yml", 30),               # pytest pyramid completes in <20s
        ("mutation-test.yml", 360),   # mutmut is the long pole, 6h max
    ],
)
def test_critical_workflows_have_timeout(wf, max_minutes):
    """Pin a timeout-minutes ceiling on critical workflows so a
    runaway pytest hang doesn't burn the free-tier 6-hour budget."""
    path = WORKFLOWS_DIR / wf
    if not path.exists():
        pytest.skip(f"{wf} not present (covered by test_critical_workflows_present)")
    parsed = yaml.safe_load(path.read_text())
    seen_timeouts = []
    for job_name, job in (parsed.get("jobs") or {}).items():
        if not isinstance(job, dict) or "uses" in job:
            continue
        timeout = job.get("timeout-minutes")
        if timeout is None:
            # The repo-wide default is 360 (GitHub Actions default); we
            # only require an explicit timeout on the critical mutation
            # job. CI/release/auto-bump can rely on the implicit ceiling.
            if wf == "mutation-test.yml":
                pytest.fail(
                    f"{wf}: job {job_name!r} missing timeout-minutes; "
                    f"the nightly mutmut run MUST have an explicit ceiling"
                )
            continue
        seen_timeouts.append(timeout)
        assert timeout <= max_minutes, (
            f"{wf}: job {job_name!r} timeout {timeout}min exceeds "
            f"reasonable ceiling {max_minutes}min"
        )
