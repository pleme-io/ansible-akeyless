# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sweep tests/integration/targets/*/tasks/main.yml -- the integration
# test playbooks that ansible-test integration runs against the
# collection. Catches YAML errors before `ansible-test integration`
# does (which fails with the same parse error but inside the slow
# integration job rather than the cheap pytest job).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS_DIR = REPO_ROOT / "tests" / "integration" / "targets"

PLAYBOOK_PATHS = sorted(TARGETS_DIR.glob("*/tasks/main.yml"))


@pytest.mark.parametrize("playbook_path", PLAYBOOK_PATHS,
                         ids=lambda p: f"{p.parent.parent.name}")
def test_integration_playbook_yaml_parses(playbook_path):
    """Every integration test target's tasks/main.yml must be valid
    YAML. ansible-test integration would fail with the same error
    but inside a much slower job; catch it here."""
    text = playbook_path.read_text()
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        pytest.fail(
            f"{playbook_path.relative_to(REPO_ROOT)}: YAML parse error: {e}"
        )
    # Tasks file should parse to a list of tasks (or None for empty).
    if parsed is not None:
        assert isinstance(parsed, list), (
            f"{playbook_path.relative_to(REPO_ROOT)}: tasks/main.yml "
            f"must parse to a list, got {type(parsed).__name__}"
        )


@pytest.mark.parametrize("playbook_path", PLAYBOOK_PATHS,
                         ids=lambda p: f"{p.parent.parent.name}")
def test_integration_playbook_starts_with_yaml_directive_or_list(playbook_path):
    """Each integration test target should start with either the YAML
    directive `---` or a list-element `- ...` line (allowing for
    leading comments). Catches files truncated to empty / placeholder
    state, which would silently pass `--list-tasks` with zero tasks."""
    text = playbook_path.read_text()
    # Strip leading comments + blank lines to find the first
    # content-bearing line.
    first_content = next(
        (ln for ln in text.splitlines()
         if ln.strip() and not ln.lstrip().startswith("#")),
        "",
    )
    valid_starts = ("---", "-")
    assert any(first_content.startswith(s) for s in valid_starts), (
        f"{playbook_path.relative_to(REPO_ROOT)}: first content line "
        f"{first_content!r} doesn't look like a YAML document or list"
    )


@pytest.mark.parametrize("playbook_path", PLAYBOOK_PATHS,
                         ids=lambda p: f"{p.parent.parent.name}")
def test_integration_playbook_uses_fqcn(playbook_path):
    """Every reference to the target module in the integration
    playbook must use the full `drzln0.akeyless.<name>:` FQCN, not
    the bare `<name>:` form. Bare references rely on collection-path
    autoloading which doesn't work in some install modes (e.g. when
    invoked from outside an ansible-galaxy-installed location).
    Post-FQCN-sweep this is the pinned convention."""
    module_name = playbook_path.parent.parent.name
    text = playbook_path.read_text()
    # If the file mentions the module name at all, the bare form must
    # not appear -- only the FQCN.
    bare_pattern = f"\n      {module_name}:"
    fqcn_pattern = f"drzln0.akeyless.{module_name}:"
    if bare_pattern in text:
        # We allow bare form only when FQCN form is absent (some
        # playbooks legitimately reference other modules and reach
        # ours via the cross-module FQCN check). Defensive: if both
        # appear, that's a partial-rewrite state we want flagged.
        assert fqcn_pattern in text, (
            f"{playbook_path.relative_to(REPO_ROOT)} uses bare module "
            f"reference `{module_name}:` without FQCN. Rewrite to "
            f"`{fqcn_pattern}` -- run tests/codemod/fqcn_sweep.py."
        )
        # The lingering bare form would be ambiguous; flag it.
        # (After the sweep this shouldn't happen, but pin the
        # post-state.)
        pytest.fail(
            f"{playbook_path.relative_to(REPO_ROOT)}: still contains "
            f"a bare `{module_name}:` reference alongside the FQCN. "
            f"Re-run tests/codemod/fqcn_sweep.py."
        )
