# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep: every filter / test plugin must use the decorators
# from plugins/module_utils/akeyless_plugin_helpers.py. Pinning the
# decorator usage here prevents a future PR from bypassing the
# uniform input-validation + exception-wrapping behaviour (which is
# the whole point of the decorator suite).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FILTER_FILE = REPO_ROOT / "plugins" / "filter" / "akeyless.py"
TEST_DIR = REPO_ROOT / "plugins" / "test"
LOOKUP_DIR = REPO_ROOT / "plugins" / "lookup"
HELPERS_FILE = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"


def _has_decorator(func_node: ast.FunctionDef, name: str) -> bool:
    """True iff `func_node` has @<name> or @<name>(...) in its decorator list."""
    for deco in func_node.decorator_list:
        if isinstance(deco, ast.Name) and deco.id == name:
            return True
        if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name) and deco.func.id == name:
            return True
    return False


def _class_has_decorator(cls_node: ast.ClassDef, name: str) -> bool:
    for deco in cls_node.decorator_list:
        if isinstance(deco, ast.Name) and deco.id == name:
            return True
        if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name) and deco.func.id == name:
            return True
    return False


def _registered_filter_names(tree: ast.AST) -> set:
    """Return the keys of FilterModule.filters() return dict, parsed
    via AST so we don't need to import the module under test."""
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "FilterModule":
            for body_node in node.body:
                if (isinstance(body_node, ast.FunctionDef)
                        and body_node.name == "filters"):
                    for sub in ast.walk(body_node):
                        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                            return {
                                k.value
                                for k in sub.value.keys
                                if isinstance(k, ast.Constant) and isinstance(k.value, str)
                            }
    return set()


# ---------------------------------------------------------------------------
# Helpers module sanity
# ---------------------------------------------------------------------------


def test_helpers_module_exists():
    assert HELPERS_FILE.exists(), (
        "plugins/module_utils/akeyless_plugin_helpers.py is missing -- "
        "every filter / test / lookup plugin depends on it"
    )


def test_helpers_exports_three_decorators():
    """Pin __all__ to include the three plugin decorators."""
    tree = ast.parse(HELPERS_FILE.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        names = {
                            e.value
                            for e in node.value.elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str)
                        }
                        for required in ("akeyless_filter", "akeyless_test", "akeyless_lookup"):
                            assert required in names, (
                                f"akeyless_plugin_helpers.__all__ missing "
                                f"`{required}` -- removing it breaks every "
                                f"plugin that decorates with it"
                            )
                        return
    pytest.fail("akeyless_plugin_helpers.py missing __all__ assignment")


# ---------------------------------------------------------------------------
# Filter decorator usage
# ---------------------------------------------------------------------------


def test_every_registered_filter_uses_akeyless_filter_decorator():
    """Each function registered via FilterModule.filters() must carry
    @akeyless_filter (or @akeyless_filter(...))."""
    tree = ast.parse(FILTER_FILE.read_text())
    registered = _registered_filter_names(tree)
    assert registered, "FilterModule.filters() returned no parseable names"

    fn_nodes = {
        n.name: n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name in registered
    }
    missing = []
    for name in registered:
        node = fn_nodes.get(name)
        if node is None or not _has_decorator(node, "akeyless_filter"):
            missing.append(name)
    assert not missing, (
        f"these filters skip @akeyless_filter (breaks uniform input "
        f"validation + AnsibleFilterError wrapping): {missing}"
    )


def test_filter_module_imports_akeyless_filter():
    """Pin the import shape so a future search-and-replace doesn't
    accidentally drop the import line."""
    text = FILTER_FILE.read_text()
    pattern = re.compile(
        r"from\s+ansible_collections\.drzln0\.akeyless\.plugins\.module_utils"
        r"\.akeyless_plugin_helpers\s+import\s+(?:\(\s*([^)]+)\)|([^\n]+))",
        re.DOTALL,
    )
    match = pattern.search(text)
    assert match, (
        "plugins/filter/akeyless.py must import @akeyless_filter from "
        "akeyless_plugin_helpers"
    )
    body = (match.group(1) or match.group(2) or "")
    names = {n.strip().split(" as ", 1)[0].strip() for n in body.split(",") if n.strip()}
    assert "akeyless_filter" in names, (
        f"plugins/filter/akeyless.py imports akeyless_plugin_helpers but "
        f"not akeyless_filter (got {names})"
    )


# ---------------------------------------------------------------------------
# Test-plugin decorator usage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    sorted(
        p for p in TEST_DIR.glob("*.py")
        if p.name not in ("__init__.py", "akeyless.py")
    ),
    ids=lambda p: p.name,
)
def test_every_test_plugin_uses_akeyless_test_decorator(path):
    """Every per-test-file in plugins/test/ must decorate the predicate
    function with @akeyless_test -- gives uniform `non-string ->
    False` + `exception -> False` behaviour."""
    tree = ast.parse(path.read_text())
    predicate_name = path.stem  # filename stem == test function name
    fn_node = next(
        (
            n for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == predicate_name
        ),
        None,
    )
    assert fn_node is not None, (
        f"{path.name}: missing top-level def {predicate_name}(...)"
    )
    assert _has_decorator(fn_node, "akeyless_test"), (
        f"{path.name}: predicate `{predicate_name}` lacks the "
        f"@akeyless_test decorator (breaks uniform non-string -> False "
        f"behaviour)"
    )


# ---------------------------------------------------------------------------
# Lookup-plugin decorator usage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    sorted(p for p in LOOKUP_DIR.glob("*.py") if p.name != "__init__.py"),
    ids=lambda p: p.name,
)
def test_every_lookup_module_class_uses_akeyless_lookup_decorator(path):
    """Each lookup's LookupModule class must use @akeyless_lookup
    (the class decorator that injects run())."""
    tree = ast.parse(path.read_text())
    cls = next(
        (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LookupModule"),
        None,
    )
    assert cls is not None, f"{path.name}: missing LookupModule class"
    assert _class_has_decorator(cls, "akeyless_lookup"), (
        f"{path.name}: LookupModule must be decorated with @akeyless_lookup "
        f"so it gets the standard auth + per-term loop + ApiException "
        f"translation. Inlining run() means re-implementing all that."
    )


@pytest.mark.parametrize(
    "path",
    sorted(p for p in LOOKUP_DIR.glob("*.py") if p.name != "__init__.py"),
    ids=lambda p: p.name,
)
def test_every_lookup_module_defines_fetch_method(path):
    """The @akeyless_lookup decorator's contract: the decorated class
    must define `fetch(self, client, token, opts, term)` (per-term)
    or `fetch(self, client, token, opts, terms)` (batch). Missing it
    raises at decoration time -- this sanity test surfaces the error
    BEFORE any plugin attempts to run."""
    tree = ast.parse(path.read_text())
    cls = next(
        (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LookupModule"),
        None,
    )
    if cls is None:
        pytest.skip("no LookupModule (covered elsewhere)")
    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    assert "fetch" in methods, (
        f"{path.name}: LookupModule missing fetch(...) method "
        f"required by @akeyless_lookup"
    )
