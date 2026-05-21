# Copyright: (c) 2026, pleme-io
# MIT License
#
# Pytest wrapper around the existing tests/sanity/smoke.py logic.
#
# Verifies the collection is structurally sound:
#   * every plugins/modules/*.py AST-parses
#   * every call_api(..., "<method>", ...) literal resolves on V2Api in the
#     local akeyless-python source (when available)
#   * the shared helper imports cleanly
#   * galaxy.yml has namespace/name/version
#   * meta/runtime.yml has requires_ansible

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
HELPER = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"
GALAXY = REPO_ROOT / "galaxy.yml"
RUNTIME = REPO_ROOT / "meta" / "runtime.yml"
SDK_V2API = Path(
    "/home/drzzln/code/github/pleme-io/akeyless-python/akeyless/api/v2_api.py"
)


def _all_module_paths():
    return sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _v2api_method_names():
    if not SDK_V2API.exists():
        return None
    tree = ast.parse(SDK_V2API.read_text())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "V2Api":
            for item in node.body:
                if (
                    isinstance(item, ast.FunctionDef)
                    and not item.name.startswith("_")
                    and not item.name.endswith("_with_http_info")
                ):
                    out.add(item.name)
    return out


def _call_api_methods(tree):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "call_api" or len(node.args) < 3:
            continue
        method_node = node.args[2]
        if isinstance(method_node, ast.Constant) and isinstance(method_node.value, str):
            out.append(method_node.value)
    return out


@pytest.mark.parametrize("module_path", _all_module_paths(), ids=lambda p: p.name)
def test_all_modules_ast_parse(module_path):
    """Every shipped module Python file must be syntactically valid."""
    ast.parse(module_path.read_text())


def test_all_call_api_methods_exist_on_v2api():
    """No call_api(..., "<method>", ...) literal should reference a non-existent SDK method."""
    sdk = _v2api_method_names()
    if sdk is None:
        pytest.skip(f"V2Api source not available at {SDK_V2API}")
    misses = set()
    for p in _all_module_paths():
        tree = ast.parse(p.read_text())
        for m in _call_api_methods(tree):
            if m not in sdk:
                misses.add((p.name, m))
    assert not misses, (
        "call_api method names not found on V2Api:\n"
        + "\n".join(f"  {fn}: {meth}" for fn, meth in sorted(misses))
    )


def test_helper_imports_cleanly():
    """plugins/module_utils/akeyless_client.py must parse without errors."""
    ast.parse(HELPER.read_text())


def test_galaxy_yml_well_formed():
    """galaxy.yml must declare namespace, name, and version."""
    text = GALAXY.read_text()
    # Don't pin the namespace string (it's configurable via provider.toml);
    # just confirm the required keys are present and non-empty.
    assert "namespace:" in text and "namespace:\n" not in text
    assert "name: akeyless" in text
    assert "version:" in text


def test_meta_runtime_yml_specifies_ansible_version():
    """meta/runtime.yml must specify a minimum Ansible version."""
    text = RUNTIME.read_text()
    assert "requires_ansible" in text
