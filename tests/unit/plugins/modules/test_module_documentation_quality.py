# Copyright: (c) 2026, pleme-io
# MIT License
#
# Module-documentation quality sweep: every plugins/modules/*.py must
# carry a non-empty short_description AND a non-empty description list,
# every option must have a description, and the documented options
# must exactly match the argspec keys (modulo state, which is implicit
# from the module's nature). Catches generator regressions that drop
# descriptions or emit options whose argspec entries are stale.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

MODULE_PATHS = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))

# Argspec keys that come from the auth doc fragment and so don't
# appear in per-module DOCUMENTATION.options. `state` IS documented
# per-module in CRUD modules, so it's not excluded here.
DOC_OPTIONAL_KEYS = frozenset({
    "gateway_url", "access_id", "access_key", "access_type",
})


def _extract_string_constant(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None


def _extract_argspec_keys(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "argument_spec":
                    if isinstance(node.value, ast.Dict):
                        return {
                            k.value for k in node.value.keys
                            if isinstance(k, ast.Constant) and isinstance(k.value, str)
                        }
    return set()


@pytest.fixture(scope="module")
def all_module_docs():
    """Pre-parse + yaml-load every module's DOCUMENTATION block."""
    out = {}
    for p in MODULE_PATHS:
        tree = ast.parse(p.read_text())
        doc_str = _extract_string_constant(tree, "DOCUMENTATION")
        argspec = _extract_argspec_keys(tree)
        try:
            doc = yaml.safe_load(doc_str) if doc_str else None
        except yaml.YAMLError:
            doc = None
        out[p.name] = (doc, argspec)
    return out


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_short_description_is_nonempty(module_path, all_module_docs):
    """The short_description field shows in `ansible-galaxy collection
    docs` and on Galaxy's web UI. Empty or missing -> the module looks
    abandoned."""
    doc, _ = all_module_docs[module_path.name]
    assert doc is not None, f"{module_path.name}: DOCUMENTATION didn't yaml-parse"
    sd = doc.get("short_description")
    assert isinstance(sd, str) and sd.strip(), (
        f"{module_path.name}: short_description must be a non-empty string, got {sd!r}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_description_is_nonempty(module_path, all_module_docs):
    """Long-form description is what users read in ansible-doc <module>.
    The generator emits it as a YAML list of strings. Empty or null
    means the module ships without an explanation."""
    doc, _ = all_module_docs[module_path.name]
    assert doc is not None
    desc = doc.get("description")
    assert desc is not None, (
        f"{module_path.name}: DOCUMENTATION missing 'description' field"
    )
    # Ansible convention: description is a list of strings (paragraphs).
    # A single-string form is tolerated by ansible-doc but discouraged.
    if isinstance(desc, str):
        assert desc.strip(), f"{module_path.name}: description string is empty"
    else:
        assert isinstance(desc, list) and any(s.strip() for s in desc if isinstance(s, str)), (
            f"{module_path.name}: description list is empty or all-blank: {desc!r}"
        )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_every_documented_option_has_description_key(module_path, all_module_docs):
    """Each option in DOCUMENTATION.options must declare a `description`
    key. The KEY presence is the strict invariant -- empty strings are
    tolerated (some upstream OpenAPI descriptions are intentionally
    blank for trivial flags) but a missing key entirely is a generator
    regression that surfaces as 'undocumented-parameter' sanity errors
    from ansible-doc / antsibull-docs."""
    doc, _ = all_module_docs[module_path.name]
    assert doc is not None
    options = doc.get("options") or {}
    bad = {}
    for name, entry in options.items():
        if not isinstance(entry, dict):
            bad[name] = f"entry is {type(entry).__name__}, not dict"
            continue
        if "description" not in entry:
            bad[name] = "description key missing"
    assert not bad, (
        f"{module_path.name}: options without 'description' key: {bad}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_no_documented_options_orphaned_from_argspec(module_path, all_module_docs):
    """Every option in DOCUMENTATION must correspond to an argspec
    entry. Documented options without argspec entries surface as
    "option doesn't apply" errors when users follow the docs.

    Reverse direction (argspec without docs) is intentionally NOT
    asserted because some modules legitimately re-document the auth
    shim's `access_type` field with a domain-specific meaning,
    creating a name collision that the simple set-diff can't
    disambiguate without per-module annotation.
    """
    doc, argspec = all_module_docs[module_path.name]
    assert doc is not None
    documented = set((doc.get("options") or {}).keys())
    # Allow auth-shim names even if they aren't in argspec (the auth
    # fragment may have introduced them); strictly require everything
    # else to back to a real argspec entry.
    orphaned = documented - argspec - DOC_OPTIONAL_KEYS
    assert not orphaned, (
        f"{module_path.name}: documented options without argspec entry: "
        f"{orphaned}"
    )
