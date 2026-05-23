# Copyright: (c) 2026, pleme-io
# MIT License
#
# Load every plugins/modules/*.py via importlib with akeyless stubbed,
# then introspect the module's argument_spec to assert structural sanity.
#
# Catches a class of regressions the AST-only test_module_shape suite
# can't see: e.g. a typo that makes argument_spec resolve to something
# other than a dict at runtime, or an argspec entry with an invalid
# `type` value that AnsibleModule would reject at runtime.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

# AnsibleModule's accepted argspec types. Anything outside this set will
# cause AnsibleModule construction to fail at runtime with
# "invalid type for argument_spec field <name>".
VALID_ARGSPEC_TYPES = frozenset({
    "str", "list", "dict", "bool", "int", "float", "path",
    "raw", "jsonarg", "json", "bytes", "bits",
})

# Every generated module declares the four auth fields. If any one is
# missing post-load, the SDK auth shim in get_client would fail.
REQUIRED_AUTH_KEYS = frozenset({
    "gateway_url", "access_id", "access_key", "access_type",
})

MODULE_PATHS = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _install_collection_helper_path():
    """Make `from ansible_collections.drzln0.akeyless...akeyless_client`
    resolve to the local helper file (sans collection install)."""
    parents = [
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ]
    for name in parents:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    helper_path = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"
    full = (
        "ansible_collections.drzln0.akeyless"
        ".plugins.module_utils.akeyless_client"
    )
    if full not in sys.modules:
        spec = importlib.util.spec_from_file_location(full, helper_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)


@pytest.fixture(scope="session", autouse=True)
def _bootstrap():
    """Install fake akeyless + AnsibleModule + helper symlink once
    per test session. Conftest's `fake_akeyless` and `fake_ansible_module`
    are function-scoped so we can't reuse them at module scope; we
    install our own minimal stubs that survive across all 208 modules.
    """
    from unittest.mock import MagicMock

    # 1. Stub akeyless package so the helper's `import akeyless` succeeds.
    if "akeyless" not in sys.modules:
        akeyless_mod = types.ModuleType("akeyless")
        akeyless_mod.__getattr__ = lambda name: MagicMock(name=f"akeyless.{name}")  # type: ignore[attr-defined]
        akeyless_mod.Configuration = MagicMock(name="akeyless.Configuration")
        akeyless_mod.ApiClient = MagicMock(name="akeyless.ApiClient")
        akeyless_mod.V2Api = MagicMock(name="akeyless.V2Api")
        akeyless_mod.Auth = MagicMock(name="akeyless.Auth")
        exc_mod = types.ModuleType("akeyless.exceptions")
        exc_mod.ApiException = type("ApiException", (Exception,), {
            "__init__": lambda self, status=None, body=None, reason=None: (
                Exception.__init__(self, reason or body or "ApiException"),
                setattr(self, "status", status),
                setattr(self, "body", body),
                setattr(self, "reason", reason),
            ) and None,
        })
        akeyless_mod.exceptions = exc_mod
        sys.modules["akeyless"] = akeyless_mod
        sys.modules["akeyless.exceptions"] = exc_mod

    # 2. Stub ansible.module_utils.basic.AnsibleModule. Modules import
    #    AnsibleModule indirectly via the helper, but loading + reading
    #    .argument_spec doesn't actually instantiate AnsibleModule, so
    #    a no-op stub class suffices.
    if "ansible.module_utils.basic" not in sys.modules:
        ans = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
        util = sys.modules.setdefault("ansible.module_utils", types.ModuleType("ansible.module_utils"))
        basic = types.ModuleType("ansible.module_utils.basic")
        basic.AnsibleModule = MagicMock(name="AnsibleModule")
        sys.modules["ansible.module_utils.basic"] = basic
        ans.module_utils = util
        util.basic = basic

    _install_collection_helper_path()
    yield


def _load_module(path):
    """Load a generated module file as a synthetic submodule. Each test
    parameter gets a unique synthetic name to avoid leaking module-level
    state across parametrize cases."""
    spec = importlib.util.spec_from_file_location(
        f"akeyless_loadtest_{path.stem}_{id(path)}", path
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_imports_without_error(module_path):
    """Every module must be importable with the akeyless SDK stubbed.
    Catches typos / missing imports / runtime SyntaxErrors that the
    AST-only test_module_shape doesn't surface."""
    mod = _load_module(module_path)
    assert hasattr(mod, "main"), f"{module_path.name}: no main() defined post-load"


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_argspec_is_dict_with_auth_keys(module_path):
    """argument_spec at module scope must be a dict with the four auth
    keys. Generated modules declare it at module level (post-refactor);
    a couple of legacy ones may declare it inside def main() (those
    fall back to the AST test in test_module_shape)."""
    mod = _load_module(module_path)
    argspec = getattr(mod, "argument_spec", None)
    if argspec is None:
        pytest.skip("argument_spec defined inside main() (legacy shape)")
    assert isinstance(argspec, dict), (
        f"{module_path.name}: argument_spec is {type(argspec).__name__}, not dict"
    )
    missing_auth = REQUIRED_AUTH_KEYS - set(argspec)
    assert not missing_auth, (
        f"{module_path.name}: argument_spec missing auth keys {missing_auth}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_argspec_types_are_all_valid(module_path):
    """Every argspec entry's `type` must be one AnsibleModule accepts.
    Catches generator regressions that emit non-existent types like
    'integer' (vs 'int') or 'string' (vs 'str')."""
    mod = _load_module(module_path)
    argspec = getattr(mod, "argument_spec", None)
    if argspec is None:
        pytest.skip("argument_spec defined inside main() (legacy shape)")
    invalid = {}
    for name, entry in argspec.items():
        if not isinstance(entry, dict):
            invalid[name] = f"entry is {type(entry).__name__}, expected dict"
            continue
        ty = entry.get("type")
        if ty is None:
            # AnsibleModule defaults missing type to 'str'; this is valid.
            continue
        if ty not in VALID_ARGSPEC_TYPES:
            invalid[name] = f"type={ty!r} not in {sorted(VALID_ARGSPEC_TYPES)}"
    assert not invalid, (
        f"{module_path.name}: invalid argspec types: {invalid}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_argspec_required_entries_are_typed(module_path):
    """Any entry marked required=True must also declare a type (else
    AnsibleModule's required-check happens before its type-coerce, and
    the user sees a useless 'argument <x> is required' for a field that
    isn't actually missing)."""
    mod = _load_module(module_path)
    argspec = getattr(mod, "argument_spec", None)
    if argspec is None:
        pytest.skip("argument_spec defined inside main() (legacy shape)")
    bad = [
        name for name, entry in argspec.items()
        if isinstance(entry, dict)
        and entry.get("required") is True
        and entry.get("type") is None
    ]
    # str is implicit but flag it for clarity. Empty by current convention.
    assert not bad, (
        f"{module_path.name}: required argspec entries without explicit type: {bad}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_access_key_marked_no_log(module_path):
    """access_key carries the secret half of the auth pair. Every module
    must mark it no_log=True so Ansible's logger redacts it from
    -vvv output and from the playbook recap."""
    mod = _load_module(module_path)
    argspec = getattr(mod, "argument_spec", None)
    if argspec is None:
        pytest.skip("argument_spec defined inside main() (legacy shape)")
    access_key = argspec.get("access_key")
    if access_key is None:
        pytest.skip("no access_key entry (impossible for generated modules)")
    assert isinstance(access_key, dict) and access_key.get("no_log") is True, (
        f"{module_path.name}: access_key argspec missing 'no_log': True "
        f"(got {access_key})"
    )
