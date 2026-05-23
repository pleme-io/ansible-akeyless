# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for the shared auth helper in
# plugins/module_utils/akeyless_lookup_auth.py. The helper exists
# specifically to DRY up the auth dance across multiple lookup +
# inventory plugins. If a future PR inlines the auth call in a single
# lookup, the DRY guarantee silently breaks and we end up with two
# divergent auth paths -- so we pin the import structure here.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOKUP_DIR = REPO_ROOT / "plugins" / "lookup"
INVENTORY_DIR = REPO_ROOT / "plugins" / "inventory"
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"

EXPECTED_HELPER_NAME = "authenticated_client"
# Matches both single-line and parenthesised multi-line `from ... import (...)`
# forms. The capture group is the contents between `import` and the
# matching close paren (or end-of-line for the single-line form).
EXPECTED_HELPER_IMPORT_RE = re.compile(
    r"from\s+ansible_collections\.drzln0\.akeyless\.plugins\.module_utils"
    r"\.akeyless_lookup_auth\s+import\s+(?:\(\s*([^)]+)\)|([^\n]+))",
    re.DOTALL,
)


def _import_names(text: str):
    """Return the set of original (un-aliased) names imported from
    akeyless_lookup_auth, or None if no such import is found.
    `from foo import bar as baz` yields {'bar'}, not {'baz'} -- callers
    care about which helper symbols are pulled in, not what they're
    locally renamed to."""
    match = EXPECTED_HELPER_IMPORT_RE.search(text)
    if not match:
        return None
    body = match.group(1) or match.group(2) or ""
    names = set()
    for raw in body.split(","):
        token = raw.strip()
        if not token:
            continue
        # Strip `as <alias>` suffix.
        name = token.split(" as ", 1)[0].strip()
        names.add(name)
    return names


def _lookup_files():
    """Yield .py files in plugins/lookup/, excluding __init__.py."""
    for path in sorted(LOOKUP_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        yield path


def _inventory_files():
    for path in sorted(INVENTORY_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        yield path


# ---------------------------------------------------------------------------
# Helper module surface
# ---------------------------------------------------------------------------


def test_helper_module_exists():
    """The shared helper file must exist. Removing it without inlining
    fallbacks breaks every lookup at import time."""
    assert HELPER_PATH.exists(), (
        f"plugins/module_utils/akeyless_lookup_auth.py is missing; "
        f"3 lookup plugins import from it"
    )


def test_helper_exports_authenticated_client():
    """`authenticated_client(opts) -> (V2Api, token)` is the single
    callable the lookups + inventory plugin call. Renaming or removing
    it silently breaks downstream callers (they import-fail with a
    cryptic ImportError, not a friendly message)."""
    tree = ast.parse(HELPER_PATH.read_text())
    defined = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    assert EXPECTED_HELPER_NAME in defined, (
        f"akeyless_lookup_auth.py missing `{EXPECTED_HELPER_NAME}` "
        f"function (defined: {sorted(defined)})"
    )


# ---------------------------------------------------------------------------
# Cross-plugin consumption
# ---------------------------------------------------------------------------


_DECORATOR_RE = re.compile(r"@akeyless_lookup\b")
_DECORATOR_IMPORT_RE = re.compile(
    r"from\s+ansible_collections\.drzln0\.akeyless\.plugins\.module_utils"
    r"\.akeyless_plugin_helpers\s+import\s+(?:\(\s*([^)]+)\)|([^\n]+))",
    re.DOTALL,
)


@pytest.mark.parametrize(
    "path",
    list(_lookup_files()),
    ids=lambda p: p.name,
)
def test_lookup_uses_decorator_or_imports_helper(path):
    """Each lookup must either use the @akeyless_lookup class decorator
    (preferred -- the decorator calls authenticated_client transitively)
    OR import authenticated_client directly. Inlining the auth call ->
    two divergent auth paths -> the DRY guarantee dies silently.

    The decorator path is the modern shape (lookups land via
    @akeyless_lookup(per_term=...) from
    plugins/module_utils/akeyless_plugin_helpers.py). The direct-import
    path remains supported for special cases that need to bypass the
    standard per-term loop."""
    text = path.read_text()
    if _DECORATOR_RE.search(text):
        # Decorator-using lookup must also import the decorator.
        helper_match = _DECORATOR_IMPORT_RE.search(text)
        assert helper_match, (
            f"{path.name}: uses @akeyless_lookup but does not import it "
            f"from ansible_collections.<...>.akeyless_plugin_helpers"
        )
        body = helper_match.group(1) or helper_match.group(2) or ""
        names = {
            n.strip().split(" as ", 1)[0].strip()
            for n in body.split(",")
            if n.strip()
        }
        assert "akeyless_lookup" in names, (
            f"{path.name}: imports from akeyless_plugin_helpers but "
            f"doesn't pull in akeyless_lookup (got {names})"
        )
        return

    # Fallback: direct authenticated_client import path.
    names = _import_names(text)
    assert names is not None, (
        f"{path.name}: must EITHER use @akeyless_lookup (preferred) OR "
        f"import `authenticated_client` from akeyless_lookup_auth directly"
    )
    assert EXPECTED_HELPER_NAME in names, (
        f"{path.name}: imports from akeyless_lookup_auth but doesn't "
        f"pull in `{EXPECTED_HELPER_NAME}` (got {names})"
    )


@pytest.mark.parametrize(
    "path",
    list(_lookup_files()),
    ids=lambda p: p.name,
)
def test_lookup_does_not_inline_v2api_auth(path):
    """Lookups MUST go through authenticated_client; an inlined
    `V2Api(...)` or `akeyless.Configuration(...)` call in a lookup
    means someone bypassed the helper."""
    text = path.read_text()
    # Allow the import line itself (V2Api may be re-imported via the
    # helper module), but reject any `V2Api(` constructor call or
    # `akeyless.Configuration(` outside of comments.
    for forbidden in ("V2Api(", "akeyless.Configuration(", "akeyless.ApiClient("):
        # Strip out lines that are comments or docstring content.
        relevant_lines = [
            line
            for line in text.splitlines()
            if not line.lstrip().startswith("#")
        ]
        relevant = "\n".join(relevant_lines)
        assert forbidden not in relevant, (
            f"{path.name}: appears to inline `{forbidden}` constructor; "
            f"use authenticated_client(opts) from akeyless_lookup_auth "
            f"instead so the auth dance stays DRY"
        )


# ---------------------------------------------------------------------------
# Inventory consumption (the 4th caller)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    list(_inventory_files()),
    ids=lambda p: p.name,
)
def test_inventory_imports_shared_helper(path):
    """The inventory plugin's auth path is identical to the lookups'.
    Same DRY guarantee applies."""
    names = _import_names(path.read_text())
    assert names is not None, (
        f"{path.name}: inventory plugin missing import of shared helper "
        f"`authenticated_client`"
    )
    assert EXPECTED_HELPER_NAME in names, (
        f"{path.name}: imports from helper but doesn't pull in "
        f"`{EXPECTED_HELPER_NAME}` (got {names})"
    )
