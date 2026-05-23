# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep for the per-filter file structure. Each filter
# registered in plugins/filter/akeyless.py's FilterModule.filters()
# must have a sibling plugins/filter/<name>.py with its own
# DOCUMENTATION block + FilterModule that registers just that filter.
#
# Why the structure exists: antsibull-docs's collection-docs format
# expects per-file filter modules for documentation rendering. A
# single-file FilterModule with N filters renders as N "Did not
# return correct DOCUMENTATION" lint errors. The per-file files
# carry the docs; the akeyless.py file holds the shared impls.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FILTER_DIR = REPO_ROOT / "plugins" / "filter"
SHARED_IMPL = FILTER_DIR / "akeyless.py"


def _registered_filter_names() -> set:
    """Parse the shared akeyless.py FilterModule.filters() return dict
    and return the set of declared filter names."""
    tree = ast.parse(SHARED_IMPL.read_text())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "FilterModule":
            for body_node in node.body:
                if isinstance(body_node, ast.FunctionDef) and body_node.name == "filters":
                    for sub in ast.walk(body_node):
                        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                            return {
                                k.value
                                for k in sub.value.keys
                                if isinstance(k, ast.Constant) and isinstance(k.value, str)
                            }
    return set()


REGISTERED = _registered_filter_names()


@pytest.mark.parametrize("name", sorted(REGISTERED), ids=lambda n: n)
def test_per_filter_file_exists(name):
    """Every registered filter must have plugins/filter/<name>.py."""
    per_file = FILTER_DIR / f"{name}.py"
    assert per_file.exists(), (
        f"plugins/filter/{name}.py is missing -- antsibull-docs expects "
        f"per-file filter modules with their own DOCUMENTATION block"
    )


@pytest.mark.parametrize("name", sorted(REGISTERED), ids=lambda n: n)
def test_per_filter_file_has_documentation(name):
    """The per-file module must carry a DOCUMENTATION block (any of the
    triple-quote styles); antsibull-docs lints that string."""
    per_file = FILTER_DIR / f"{name}.py"
    if not per_file.exists():
        pytest.skip("per-file missing (covered by earlier test)")
    text = per_file.read_text()
    match = re.search(
        r'^DOCUMENTATION\s*=\s*[rRuU]?(\'\'\'|""")',
        text,
        re.MULTILINE,
    )
    assert match, (
        f"plugins/filter/{name}.py missing DOCUMENTATION = ... block"
    )


@pytest.mark.parametrize("name", sorted(REGISTERED), ids=lambda n: n)
def test_per_filter_file_doc_name_matches_filename(name):
    """The DOCUMENTATION `name:` field must match the filename stem
    -- otherwise ansible-doc can't resolve drzln0.akeyless.<name>."""
    import yaml
    per_file = FILTER_DIR / f"{name}.py"
    if not per_file.exists():
        pytest.skip("per-file missing")
    text = per_file.read_text()
    match = re.search(
        r'^DOCUMENTATION\s*=\s*[rRuU]?(?P<q>\'\'\'|""")(?P<body>.*?)(?P=q)',
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert match, f"plugins/filter/{name}.py missing DOCUMENTATION block"
    doc = yaml.safe_load(match.group("body"))
    assert isinstance(doc, dict), (
        f"plugins/filter/{name}.py: DOCUMENTATION must parse to a dict"
    )
    assert doc.get("name") == name, (
        f"plugins/filter/{name}.py: DOCUMENTATION name={doc.get('name')!r} "
        f"must match filename stem {name!r}"
    )


@pytest.mark.parametrize("name", sorted(REGISTERED), ids=lambda n: n)
def test_per_filter_file_registers_via_filtermodule(name):
    """Each per-file module must declare a FilterModule class that
    registers exactly its one filter -- mirrors how community.general
    + community.crypto structure per-filter docs."""
    per_file = FILTER_DIR / f"{name}.py"
    if not per_file.exists():
        pytest.skip("per-file missing")
    tree = ast.parse(per_file.read_text())
    fm = next(
        (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "FilterModule"),
        None,
    )
    assert fm is not None, (
        f"plugins/filter/{name}.py missing class FilterModule"
    )
    # Inspect filters() to confirm it registers the right name.
    for body_node in fm.body:
        if isinstance(body_node, ast.FunctionDef) and body_node.name == "filters":
            for sub in ast.walk(body_node):
                if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                    registered = {
                        k.value
                        for k in sub.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)
                    }
                    assert name in registered, (
                        f"plugins/filter/{name}.py FilterModule.filters() must "
                        f"register {name!r} (got {registered})"
                    )
                    return
    pytest.fail(
        f"plugins/filter/{name}.py FilterModule missing filters() method"
    )


def test_no_extra_per_filter_files_without_registration():
    """The other direction: every plugins/filter/<name>.py file (other
    than akeyless.py + __init__.py) must correspond to a registered
    filter. Catches a per-file module added without wiring it through
    FilterModule.filters() in the shared impl."""
    per_file_stems = {
        p.stem
        for p in FILTER_DIR.glob("*.py")
        if p.name not in ("__init__.py", "akeyless.py")
    }
    extras = per_file_stems - REGISTERED
    assert not extras, (
        f"these per-filter files exist but aren't registered in "
        f"plugins/filter/akeyless.py's FilterModule.filters(): {extras}"
    )
