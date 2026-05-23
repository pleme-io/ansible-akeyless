# Copyright: (c) 2026, pleme-io
# MIT License
#
# Architectural invariant: post-refactor, no module under
# plugins/modules/*.py should import AnsibleModule directly. The
# lifecycle helpers (run_standard_crud / run_action_module /
# run_info_module) construct AnsibleModule internally so per-module
# code stays declarative.
#
# This test pins that architecture so a regression (e.g. a hand-
# patched module reintroducing the legacy boilerplate) gets caught
# in CI rather than at next-regen-overwrite time.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

MODULE_PATHS = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _find_imports(tree: ast.AST):
    """Yield (module_path_str, names) for every `from X import a, b`
    statement, plus (name, None) for every `import X` statement."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            yield node.module or "", [a.name for a in node.names]
        elif isinstance(node, ast.Import):
            for a in node.names:
                yield a.name, None


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_no_direct_ansible_module_import(module_path):
    """Post-refactor: AnsibleModule construction lives inside the
    lifecycle helpers. A module importing AnsibleModule directly is
    either legacy boilerplate that escaped the codemod OR someone
    bypassed the helper -- both regressions worth catching."""
    tree = ast.parse(module_path.read_text())
    for module_name, imports in _find_imports(tree):
        if (
            module_name == "ansible.module_utils.basic"
            and imports
            and "AnsibleModule" in imports
        ):
            pytest.fail(
                f"{module_path.name}: imports AnsibleModule directly from "
                f"ansible.module_utils.basic. Post-refactor, this should go "
                f"through run_standard_crud / run_action_module / "
                f"run_info_module instead."
            )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_imports_only_from_akeyless_client(module_path):
    """Every generated module should import EXACTLY one external symbol
    source: ansible_collections.<ns>.<name>.plugins.module_utils.
    akeyless_client. The shape:
       from ansible_collections.drzln0.akeyless.plugins.module_utils
            .akeyless_client import (run_*_module,)

    Catches regressions where a module sneaks in unrelated dependencies
    (e.g. requests, json, manually importing the SDK) that would pull
    runtime dependencies the collection's requirements.txt doesn't
    declare."""
    tree = ast.parse(module_path.read_text())

    # Allow the standard `from __future__ import absolute_import, ...`
    # idiom that every module ships with.
    allowed_modules = {
        "__future__",  # absolute_import / division / print_function
        # The collection helper import path -- the only thing modules
        # should actually pull in.
        "ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client",
    }

    for module_name, imports in _find_imports(tree):
        if module_name in allowed_modules:
            continue
        if module_name.startswith("ansible_collections.drzln0.akeyless.plugins.module_utils"):
            continue
        pytest.fail(
            f"{module_path.name}: imports from {module_name!r} -- only the "
            f"akeyless_client helper + __future__ are allowed. Imports must "
            f"route through the helper so runtime dependencies stay declared "
            f"in requirements.txt."
        )
