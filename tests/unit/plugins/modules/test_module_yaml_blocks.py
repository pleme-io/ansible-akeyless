# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sweep every plugins/modules/*.py for the three YAML-embedded-in-
# Python blocks (DOCUMENTATION / EXAMPLES / RETURN). antsibull-docs +
# ansible-doc parse these at install time; YAML errors fail with
# cryptic stack traces. Catch them upstream of release.
#
# 3 sweeps x 208 modules = 624 parametrized cases.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

MODULE_PATHS = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _extract_string_constant(tree: ast.AST, name: str):
    """Find a module-level assignment `NAME = "..."` (or r'''...''') and
    return the string value. Returns None if the constant is absent."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return node.value.value
    return None


@pytest.fixture(scope="module")
def all_module_trees():
    """Pre-parse every module's AST once per test session."""
    return {p.name: ast.parse(p.read_text()) for p in MODULE_PATHS}


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_documentation_yaml_parses(module_path, all_module_trees):
    """The DOCUMENTATION block is the source for `ansible-doc <module>`
    and Galaxy's online docs. YAML errors here mean the module silently
    has no docs in the published collection."""
    doc = _extract_string_constant(all_module_trees[module_path.name], "DOCUMENTATION")
    assert doc is not None, f"{module_path.name}: no DOCUMENTATION constant"
    try:
        parsed = yaml.safe_load(doc)
    except yaml.YAMLError as e:
        pytest.fail(f"{module_path.name}: DOCUMENTATION YAML invalid: {e}")
    assert isinstance(parsed, dict), (
        f"{module_path.name}: DOCUMENTATION must parse to a dict, "
        f"got {type(parsed).__name__}"
    )
    # The module-level `module:` key is what ansible-doc dispatches on.
    assert parsed.get("module") == module_path.stem, (
        f"{module_path.name}: DOCUMENTATION module={parsed.get('module')!r}, "
        f"expected {module_path.stem!r} (filename match)"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_examples_yaml_parses(module_path, all_module_trees):
    """The EXAMPLES block is a YAML list of tasks. ansible-doc renders
    it verbatim; a YAML error means users see a parse traceback when
    they run `ansible-doc <module>`."""
    examples = _extract_string_constant(all_module_trees[module_path.name], "EXAMPLES")
    assert examples is not None, f"{module_path.name}: no EXAMPLES constant"
    try:
        parsed = yaml.safe_load(examples)
    except yaml.YAMLError as e:
        pytest.fail(f"{module_path.name}: EXAMPLES YAML invalid: {e}")
    # EXAMPLES should be a list of dict-shaped tasks. Allow None for
    # info modules that legitimately have a single placeholder example
    # parsing to None (rare but valid YAML).
    if parsed is not None:
        assert isinstance(parsed, list), (
            f"{module_path.name}: EXAMPLES must parse to a list (of tasks), "
            f"got {type(parsed).__name__}"
        )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_return_yaml_parses(module_path, all_module_trees):
    """The RETURN block declares the module's response shape. A YAML
    error fails `ansible-doc <module> --json` and downstream automation
    that introspects collection docs."""
    return_block = _extract_string_constant(all_module_trees[module_path.name], "RETURN")
    assert return_block is not None, f"{module_path.name}: no RETURN constant"
    # RETURN may legitimately be a yaml-comment-only block ("# No computed
    # fields") in which case yaml.safe_load returns None. That's a valid
    # parse -- the block declares no return fields.
    try:
        yaml.safe_load(return_block)
    except yaml.YAMLError as e:
        pytest.fail(f"{module_path.name}: RETURN YAML invalid: {e}")
