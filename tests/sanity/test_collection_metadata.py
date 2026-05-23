# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for meta/ + plugins/doc_fragments/ -- the collection-
# level metadata that drives ansible-core compatibility detection and
# antsibull-docs rendering. Easy to break in PRs that touch the helper
# without realizing the doc fragment + runtime constraint move in
# lockstep with it.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
META_RUNTIME = REPO_ROOT / "meta" / "runtime.yml"
AUTH_FRAGMENT = REPO_ROOT / "plugins" / "doc_fragments" / "auth.py"

# Every option carried by the auth doc fragment must surface on every
# generated module's argspec (see test_module_loads). Pin the minimum
# set here so a doc-fragment slim-down doesn't silently de-document
# parameters the modules still expose.
REQUIRED_AUTH_OPTIONS = frozenset({
    "gateway_url", "access_id", "access_key", "access_type",
})


@pytest.fixture(scope="module")
def runtime_manifest():
    return yaml.safe_load(META_RUNTIME.read_text())


def test_meta_runtime_exists_and_parses(runtime_manifest):
    assert isinstance(runtime_manifest, dict), (
        f"meta/runtime.yml must parse to a dict, got {type(runtime_manifest).__name__}"
    )


def test_meta_runtime_requires_ansible_is_set(runtime_manifest):
    """ansible-core uses this constraint to refuse installation on
    incompatible versions; missing this means the collection installs
    on truly anything and breaks at runtime instead."""
    constraint = runtime_manifest.get("requires_ansible")
    assert constraint, "meta/runtime.yml missing requires_ansible"
    # PEP 440-ish version spec; ansible-core uses pip-style operators.
    assert re.match(r"^[><=!~]{1,2}[\d.]+", constraint), (
        f"requires_ansible={constraint!r} not a valid version constraint"
    )


def test_meta_runtime_pins_minimum_ansible(runtime_manifest):
    """The minimum-Ansible declaration should match the flake.nix
    minAnsibleVersion line so a release published under a newer
    minimum doesn't silently work on older runtimes."""
    constraint = runtime_manifest.get("requires_ansible", "")
    # The current floor is 2.14.0. If we move to 2.15 / 2.16, both
    # this assertion and flake.nix update together.
    assert constraint == ">=2.14.0", (
        f"requires_ansible={constraint!r}; if intentionally bumping, "
        f"update both meta/runtime.yml AND flake.nix minAnsibleVersion."
    )


# ---------------------------------------------------------------------------
# doc_fragments/auth.py
# ---------------------------------------------------------------------------


def _load_auth_fragment():
    spec = importlib.util.spec_from_file_location("auth_doc_fragment", AUTH_FRAGMENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def auth_fragment():
    return _load_auth_fragment()


def test_doc_fragment_loads_and_exposes_classdef(auth_fragment):
    """Ansible's antsibull-docs walks the `ModuleDocFragment` class on
    every fragment file. Missing the class or renaming it breaks doc
    generation for every module that does
    `extends_documentation_fragment: drzln0.akeyless.auth`."""
    cls = getattr(auth_fragment, "ModuleDocFragment", None)
    assert cls is not None and isinstance(cls, type), (
        "doc_fragments/auth.py must define a top-level `ModuleDocFragment` class"
    )


def test_doc_fragment_DOCUMENTATION_yaml_parses(auth_fragment):
    """The class's DOCUMENTATION string is YAML embedded inside Python.
    YAML errors here surface as cryptic ansible-doc failures rather
    than friendly Python tracebacks; parse it here for early signal."""
    docs = getattr(auth_fragment.ModuleDocFragment, "DOCUMENTATION", None)
    assert isinstance(docs, str), (
        "ModuleDocFragment.DOCUMENTATION must be a string"
    )
    parsed = yaml.safe_load(docs)
    assert isinstance(parsed, dict), (
        f"DOCUMENTATION must parse to a dict, got {type(parsed).__name__}"
    )
    assert "options" in parsed, "DOCUMENTATION missing top-level 'options' key"


def test_doc_fragment_documents_every_auth_option(auth_fragment):
    """Every argspec field referenced by the auth shim must appear in
    the doc fragment's options map. Missing fragment entries surface
    as 'undocumented-parameter' sanity failures."""
    docs = yaml.safe_load(auth_fragment.ModuleDocFragment.DOCUMENTATION)
    documented = set(docs.get("options", {}))
    missing = REQUIRED_AUTH_OPTIONS - documented
    assert not missing, (
        f"doc_fragments/auth.py missing options for: {missing}; "
        f"every module exposes these in its argspec via the auth shim, "
        f"so they must be documented in this fragment"
    )


def test_doc_fragment_each_option_has_description_and_type(auth_fragment):
    """Each documented option needs a description (for users) and a
    type (for sanity validation). Missing either fails ansible-doc
    rendering with a noisy error."""
    docs = yaml.safe_load(auth_fragment.ModuleDocFragment.DOCUMENTATION)
    options = docs.get("options", {})
    bad = {}
    for name, entry in options.items():
        if not isinstance(entry, dict):
            bad[name] = "entry is not a dict"
            continue
        if not entry.get("description"):
            bad[name] = "missing description"
        elif "type" not in entry:
            bad[name] = "missing type"
    assert not bad, (
        f"doc_fragments/auth.py options with missing description/type: {bad}"
    )
