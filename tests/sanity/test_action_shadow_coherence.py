# Copyright: (c) 2026, pleme-io
# MIT License
#
# Action-plugin shadow modules live in THREE places that must move in
# lockstep:
#
#   1. plugins/action/<name>.py        -- the controller-side ActionBase
#   2. plugins/modules/<name>.py       -- the no-op module wrapper that
#                                          carries DOCUMENTATION for
#                                          ansible-doc + appears in
#                                          plugins/modules sweeps
#   3. provider.toml's
#      [platforms.ansible] action_group_extras = [...]
#      OR the generator-emitted action_groups.all from meta/runtime.yml
#                                       -- so module_defaults reaches it
#
# This test pins that triad. Drift in any of the three places silently
# breaks the action plugin (wrapper invoked instead of action, or
# module_defaults not applied).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTION_DIR = REPO_ROOT / "plugins" / "action"
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
RUNTIME_YML = REPO_ROOT / "meta" / "runtime.yml"

ACTION_PLUGIN_NAMES = sorted(
    p.stem for p in ACTION_DIR.glob("*.py") if not p.name.startswith("_")
) if ACTION_DIR.is_dir() else []


@pytest.mark.parametrize("action_name", ACTION_PLUGIN_NAMES, ids=str)
def test_action_plugin_has_matching_module_wrapper(action_name):
    """For each plugins/action/<name>.py there must be a matching
    plugins/modules/<name>.py wrapper. Without the wrapper, users
    can't invoke the action via `drzln0.akeyless.<name>:` task syntax
    AND `ansible-doc` returns "no such module"."""
    wrapper = MODULES_DIR / f"{action_name}.py"
    assert wrapper.exists(), (
        f"plugins/action/{action_name}.py exists but plugins/modules/"
        f"{action_name}.py is missing -- task syntax `drzln0.akeyless."
        f"{action_name}:` won't resolve without it"
    )


@pytest.mark.parametrize("action_name", ACTION_PLUGIN_NAMES, ids=str)
def test_action_plugin_is_in_action_groups_all(action_name):
    """Action-shadow modules must appear in meta/runtime.yml
    action_groups.all so `module_defaults: group/drzln0.akeyless.all:`
    applies to them. Without this, users have to repeat auth on every
    action-plugin invocation -- silently bypassing the whole
    module_defaults pattern."""
    runtime = yaml.safe_load(RUNTIME_YML.read_text())
    declared = set((runtime.get("action_groups") or {}).get("all") or [])
    assert action_name in declared, (
        f"meta/runtime.yml action_groups.all is missing {action_name!r}. "
        f"Either add it to provider.toml's [platforms.ansible] "
        f"action_group_extras (canonical for hand-maintained action "
        f"shadows) or to action_groups.all directly."
    )


@pytest.mark.parametrize("action_name", ACTION_PLUGIN_NAMES, ids=str)
def test_action_plugin_class_name_matches_convention(action_name):
    """Ansible looks for a class named ActionModule in every action
    plugin file. Other names won't be picked up by the action loader."""
    text = (ACTION_DIR / f"{action_name}.py").read_text()
    assert "class ActionModule" in text, (
        f"plugins/action/{action_name}.py must define `class ActionModule`"
        f"; the action loader looks for that exact symbol"
    )


@pytest.mark.parametrize("action_name", ACTION_PLUGIN_NAMES, ids=str)
def test_module_wrapper_fails_loud_when_invoked_directly(action_name):
    """The module wrapper's main() should fail with a clear message if
    invoked directly (which only happens when the action plugin path
    isn't discoverable). Pin the convention: the wrapper must
    reference 'action plugin' in its message so the error explains
    what's wrong."""
    text = (MODULES_DIR / f"{action_name}.py").read_text()
    assert "action plugin" in text.lower(), (
        f"plugins/modules/{action_name}.py wrapper should reference "
        f"'action plugin' in its fail / docstring text so users hit "
        f"the wrapper see a clear 'this is an action plugin, install "
        f"the collection properly' message"
    )
