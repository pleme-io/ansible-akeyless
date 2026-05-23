# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for plugins/filter/akeyless.py registration. Filters
# don't have DOCUMENTATION YAML blocks; they're documented via per-
# function docstrings + the README's available-filters list. This file
# pins the cross-checks that prevent drift between:
#   - the FilterModule.filters() return value,
#   - the docstring-bearing top-level functions,
#   - the README's available-filters list.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import re
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FILTER_PATH = REPO_ROOT / "plugins" / "filter" / "akeyless.py"
README = REPO_ROOT / "README.md"


def _ast_tree():
    return ast.parse(FILTER_PATH.read_text())


def _toplevel_function_names():
    """Return public top-level def names (excluding _underscore helpers)."""
    return {
        node.name
        for node in _ast_tree().body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }


def _filtermodule_returned_names():
    """Parse the FilterModule.filters() method's return dict by AST and
    return the set of declared filter names (keys of the dict)."""
    for node in _ast_tree().body:
        if not (isinstance(node, ast.ClassDef) and node.name == "FilterModule"):
            continue
        for body_node in node.body:
            if not (
                isinstance(body_node, ast.FunctionDef)
                and body_node.name == "filters"
            ):
                continue
            for sub in ast.walk(body_node):
                if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                    return {
                        k.value
                        for k in sub.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)
                    }
    return set()


def _readme_filter_list():
    """Pull the 'Available filters: a, b, c' list out of the README."""
    text = README.read_text()
    match = re.search(
        r"Available filters:\s*((?:`[^`]+`(?:,|\s|and|\.)*)+)\.",
        text,
        re.DOTALL,
    )
    if not match:
        return set()
    return set(re.findall(r"`([^`]+)`", match.group(1)))


# ---------------------------------------------------------------------------
# FilterModule registration cross-checks
# ---------------------------------------------------------------------------


def test_filtermodule_declares_filters_method():
    """FilterModule.filters() is the contract Ansible's filter loader
    walks. Missing the method silently de-registers every filter and
    leaves playbooks rendering `'undefined filter: ...'`."""
    tree = _ast_tree()
    fm_class = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "FilterModule"
        ),
        None,
    )
    assert fm_class is not None, "plugins/filter/akeyless.py missing class FilterModule"
    methods = {n.name for n in fm_class.body if isinstance(n, ast.FunctionDef)}
    assert "filters" in methods, (
        "FilterModule must declare a filters() method that returns "
        "{name: callable}"
    )


def test_filter_names_match_function_names():
    """Each filter NAME in FilterModule.filters() must equal a top-level
    function defined in the same module. Catches typo'd registrations
    like {'b64decode': b64decode_secret}."""
    registered = _filtermodule_returned_names()
    defined = _toplevel_function_names()
    unknown_registrations = registered - defined
    assert not unknown_registrations, (
        f"FilterModule.filters() declares names not matching any "
        f"top-level function: {unknown_registrations}"
    )


def test_every_public_function_is_registered_as_filter():
    """The other direction: every public top-level function (no
    underscore prefix) must be wired through FilterModule.filters() --
    otherwise users can't reach it from playbooks and dead code piles
    up."""
    registered = _filtermodule_returned_names()
    defined = _toplevel_function_names()
    unregistered = defined - registered
    assert not unregistered, (
        f"plugins/filter/akeyless.py has public top-level functions not "
        f"registered as filters: {unregistered}. Either add them to "
        f"FilterModule.filters() or rename with leading underscore."
    )


def test_each_filter_function_has_docstring():
    """Filters are user-facing; lack of a docstring shows '(no docs)'
    in `ansible-doc -t filter`. Pin every registered function to have
    a non-empty docstring."""
    registered = _filtermodule_returned_names()
    bad = []
    for node in _ast_tree().body:
        if isinstance(node, ast.FunctionDef) and node.name in registered:
            docstring = ast.get_docstring(node)
            if not docstring or not docstring.strip():
                bad.append(node.name)
    assert not bad, (
        f"these registered filters have no docstring: {bad}"
    )


# ---------------------------------------------------------------------------
# README cross-check
# ---------------------------------------------------------------------------


def test_readme_filter_list_matches_filtermodule():
    """The README's 'Available filters:' line must enumerate the SAME
    filters as FilterModule.filters(). Drift here surfaces as 'the
    docs say there's a foo filter but it doesn't exist' user reports."""
    registered = _filtermodule_returned_names()
    documented = _readme_filter_list()
    only_registered = registered - documented
    only_documented = documented - registered
    assert not only_registered and not only_documented, (
        f"README ↔ FilterModule drift -- "
        f"registered but not in README: {only_registered}; "
        f"in README but not registered: {only_documented}"
    )


def test_readme_test_plugin_list_matches_reality():
    """Same drift check, for the test plugins. The README's 'Available
    tests:' list must match the per-test file names."""
    text = README.read_text()
    match = re.search(
        r"Available tests:\s*((?:`[^`]+`(?:,|\s|and|\.)*)+)\.",
        text,
        re.DOTALL,
    )
    assert match, "README missing 'Available tests:' line"
    documented = set(re.findall(r"`([^`]+)`", match.group(1)))
    test_dir = REPO_ROOT / "plugins" / "test"
    actual = {
        p.stem
        for p in test_dir.glob("*.py")
        if p.name not in ("__init__.py", "akeyless.py")
    }
    only_documented = documented - actual
    only_actual = actual - documented
    assert not only_documented and not only_actual, (
        f"README ↔ plugins/test/ drift -- "
        f"in README but no file: {only_documented}; "
        f"file exists but not in README: {only_actual}"
    )
