# Copyright: (c) 2026, pleme-io
# MIT License
#
# Pin: meta/runtime.yml's action_groups.all must match plugins/modules/
# exactly. Drift means users of `module_defaults` set auth on tasks
# that the group default isn't actually applied to (silent footgun --
# the playbook authenticates per task instead of via the group).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_YML = REPO_ROOT / "meta" / "runtime.yml"
MODULES_DIR = REPO_ROOT / "plugins" / "modules"


@pytest.fixture(scope="module")
def runtime():
    return yaml.safe_load(RUNTIME_YML.read_text())


@pytest.fixture(scope="module")
def module_names():
    """Module stems (filename minus .py) for every plugins/modules/*.py,
    excluding underscore-prefixed pseudo-modules. This is the canonical
    list action_groups.all should mirror."""
    return frozenset(
        p.stem for p in MODULES_DIR.glob("*.py")
        if not p.name.startswith("_")
    )


def test_runtime_yml_declares_action_groups(runtime):
    """The runtime manifest must carry an action_groups block.
    Missing it means users can't use group/drzln0.akeyless.all in
    module_defaults at all."""
    assert "action_groups" in runtime, (
        "meta/runtime.yml is missing top-level `action_groups` key"
    )
    assert "all" in (runtime["action_groups"] or {}), (
        "meta/runtime.yml action_groups missing the `all` group"
    )


def test_action_groups_all_has_no_stale_entries(runtime, module_names):
    """Every name in action_groups.all must correspond to a real
    plugins/modules/*.py. Stale entries (modules renamed/removed but
    not pruned from runtime.yml) confuse Ansible's resolver -- it
    silently fails to apply the group default for missing names."""
    declared = set(runtime["action_groups"]["all"])
    stale = declared - module_names
    assert not stale, (
        f"meta/runtime.yml action_groups.all has {len(stale)} stale entries "
        f"that don't correspond to a plugins/modules file: {sorted(stale)}"
    )


def test_action_groups_all_covers_every_module(runtime, module_names):
    """Every plugins/modules/*.py must appear in action_groups.all so
    `group/drzln0.akeyless.all` covers the entire module surface.
    Missing modules silently bypass the group default."""
    declared = set(runtime["action_groups"]["all"])
    missing = module_names - declared
    assert not missing, (
        f"meta/runtime.yml action_groups.all is missing {len(missing)} "
        f"module(s): {sorted(missing)}. Add them to keep `module_defaults: "
        f"group/drzln0.akeyless.all:` working for the full surface."
    )


def test_action_groups_all_is_sorted(runtime):
    """Sorted == diff-friendly: adding a new module produces a single-
    line insertion not a 200-line shuffle. Pin the sort order."""
    declared = runtime["action_groups"]["all"]
    assert declared == sorted(declared), (
        "meta/runtime.yml action_groups.all should be sorted alphabetically "
        "to keep PR diffs clean when modules are added/removed"
    )
