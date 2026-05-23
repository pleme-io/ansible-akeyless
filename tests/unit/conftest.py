# Copyright: (c) 2026, pleme-io
# MIT License
#
# Shared pytest fixtures for the akeyless collection unit tests.
#
# These fixtures install MagicMock-backed `akeyless`, `akeyless.exceptions`,
# and `ansible.module_utils.basic` into sys.modules BEFORE the module under
# test is imported. The Akeyless SDK is OpenAPI-generated and unsafe to
# import in CI (heavy dependency tree + auth side effects on construction),
# so every test that touches generated module code routes through these.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]


def install_collection_module_util(stem: str) -> types.ModuleType:
    """Load `plugins/module_utils/<stem>.py` under its canonical
    `ansible_collections.drzln0.akeyless.plugins.module_utils.<stem>`
    FQ name. Idempotent on re-call -- pops + reloads so each call
    picks up whatever fake_akeyless the current test has installed.

    Used by tests that load production plugins (filters / tests /
    lookups / etc.) whose imports reference these helpers at module
    scope.
    """
    # Ensure the parent package skeleton exists in sys.modules.
    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))

    full = f"ansible_collections.drzln0.akeyless.plugins.module_utils.{stem}"
    sys.modules.pop(full, None)  # force re-import so SDK rebinds
    helper_path = _REPO_ROOT.parent / "plugins" / "module_utils" / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(full, helper_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


class _FakeApiException(Exception):
    """Stand-in for akeyless.exceptions.ApiException with status/body/reason."""

    def __init__(self, status=None, body=None, reason=None):
        super().__init__(reason or body or "ApiException")
        self.status = status
        self.body = body
        self.reason = reason


def _install_fake_akeyless():
    """Insert a MagicMock-backed `akeyless` package into sys.modules.

    Returns the inserted (akeyless_module, exceptions_module) tuple so
    callers can re-bind specific attributes (e.g. model classes).
    """
    akeyless_mod = types.ModuleType("akeyless")
    # Every attribute access on the module returns a fresh MagicMock-like
    # callable that records args -- so build_body("CreateRole", {...})
    # can be intercepted by tests via akeyless.CreateRole.
    akeyless_mod.__getattr__ = lambda name: MagicMock(name=f"akeyless.{name}")  # type: ignore[attr-defined]
    # Provide concrete Configuration/ApiClient/V2Api/Auth so get_client can
    # call them without explosion. Tests override V2Api per case.
    akeyless_mod.Configuration = MagicMock(name="akeyless.Configuration")
    akeyless_mod.ApiClient = MagicMock(name="akeyless.ApiClient")
    akeyless_mod.V2Api = MagicMock(name="akeyless.V2Api")
    akeyless_mod.Auth = MagicMock(name="akeyless.Auth")

    exc_mod = types.ModuleType("akeyless.exceptions")
    exc_mod.ApiException = _FakeApiException
    akeyless_mod.exceptions = exc_mod

    sys.modules["akeyless"] = akeyless_mod
    sys.modules["akeyless.exceptions"] = exc_mod
    return akeyless_mod, exc_mod


@pytest.fixture
def fake_akeyless():
    """Replace `akeyless` + `akeyless.exceptions` with MagicMocks.

    Yields the (akeyless_module, exceptions_module) tuple. Restores the
    original sys.modules entries on teardown so other tests are isolated.
    """
    saved = {
        k: sys.modules.get(k) for k in ("akeyless", "akeyless.exceptions")
    }
    pkg, exc = _install_fake_akeyless()
    try:
        yield pkg, exc
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


class _ExitJsonCalled(SystemExit):
    """Raised when AnsibleModule.exit_json is invoked, with .kwargs payload."""

    def __init__(self, **kwargs):
        super().__init__(0)
        self.kwargs = kwargs


class _FailJsonCalled(SystemExit):
    """Raised when AnsibleModule.fail_json is invoked, with .kwargs payload."""

    def __init__(self, **kwargs):
        super().__init__(1)
        self.kwargs = kwargs


def _make_module_factory(params, check_mode=False):
    """Build an AnsibleModule replacement that records calls + exits via SystemExit."""

    def factory(argument_spec=None, supports_check_mode=False, **_kw):
        module = MagicMock(name="AnsibleModule")
        # Populate params from defaults in argument_spec, then user overrides.
        resolved = {}
        for key, opts in (argument_spec or {}).items():
            if isinstance(opts, dict) and "default" in opts:
                resolved[key] = opts["default"]
            else:
                resolved[key] = None
        resolved.update(params or {})
        module.params = resolved
        module.check_mode = bool(check_mode)
        module.argument_spec = argument_spec
        module.supports_check_mode = supports_check_mode

        def _exit_json(**kw):
            raise _ExitJsonCalled(**kw)

        def _fail_json(**kw):
            raise _FailJsonCalled(**kw)

        module.exit_json.side_effect = _exit_json
        module.fail_json.side_effect = _fail_json
        return module

    return factory


@pytest.fixture
def fake_ansible_module():
    """Mock `ansible.module_utils.basic.AnsibleModule`.

    Returns a helper:

        module = fake_ansible_module(params={...}, check_mode=False)

    Calls to `module.exit_json(...)` raise `ExitJsonCalled`, and
    `module.fail_json(...)` raises `FailJsonCalled`. Tests should
    pytest.raises(SystemExit) and inspect `.kwargs`.
    """
    saved = {
        k: sys.modules.get(k)
        for k in ("ansible", "ansible.module_utils", "ansible.module_utils.basic")
    }
    # Build a stub package hierarchy.
    ansible_mod = sys.modules.get("ansible") or types.ModuleType("ansible")
    util_mod = sys.modules.get("ansible.module_utils") or types.ModuleType("ansible.module_utils")
    basic_mod = types.ModuleType("ansible.module_utils.basic")

    sys.modules["ansible"] = ansible_mod
    sys.modules["ansible.module_utils"] = util_mod
    sys.modules["ansible.module_utils.basic"] = basic_mod
    ansible_mod.module_utils = util_mod
    util_mod.basic = basic_mod

    # The factory closure captures per-test params; we expose it via a
    # callable returned to the test.
    state = {"factory": None}

    def _builder(params=None, check_mode=False):
        factory = _make_module_factory(params or {}, check_mode=check_mode)
        state["factory"] = factory
        basic_mod.AnsibleModule = factory  # type: ignore[attr-defined]
        return factory

    try:
        yield _builder
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# Expose the exception classes so tests can `from conftest import ...`
# isn't possible (conftest is auto-discovered), but pytest re-exports them
# via the namespace below. Tests import via the fixtures themselves.
ExitJsonCalled = _ExitJsonCalled
FailJsonCalled = _FailJsonCalled
FakeApiException = _FakeApiException
