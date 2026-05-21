# Copyright: (c) 2026, pleme-io
# MIT License
#
# Shared fixtures for the mock-server integration tests.
#
# These tests exercise full module main() flows -- argspec resolution, auth
# dispatch, SDK call, response handling, exit_json payload -- against a
# stubbed Akeyless API surface. We use the same SDK-mock fallback that the
# unit/test_module_behavior.py tests use (the akeyless SDK's HTTP layer
# does not cleanly intercept via responses/aresponses because of its
# auto-generated body validation), but layered with a small "mock server"
# abstraction that lets each test declare endpoint contracts the way you
# would in a recorded VCR cassette.
#
# To add a new mock test:
#   1. Add a target module to MOCK_MODULES below (only if it's not already
#      loadable through the shared `mock_server` fixture).
#   2. Write tests/mock/test_<module>.py importing `mock_server`.
#   3. In each test, register endpoint responses via `mock_server.on(...)`,
#      then call `mock_server.run_module(<module>.py, params={...})` and
#      assert on the returned exit payload.
#
# See tests/mock/README.md for the full pattern.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import re
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


class _FakeApiException(Exception):
    """Match akeyless.exceptions.ApiException's status/body/reason shape."""

    def __init__(self, status=None, body=None, reason=None):
        super().__init__(reason or body or "ApiException")
        self.status = status
        self.body = body
        self.reason = reason


class _ExitJsonCalled(SystemExit):
    def __init__(self, **kwargs):
        super().__init__(0)
        self.kwargs = kwargs


class _FailJsonCalled(SystemExit):
    def __init__(self, **kwargs):
        super().__init__(1)
        self.kwargs = kwargs


# ---------------------------------------------------------------------------
# Mock server: tiny endpoint registry over the akeyless SDK V2Api facade.
# ---------------------------------------------------------------------------


class MockServer:
    """A pretend Akeyless API.

    Each call to `client.<method_name>(body)` looks up its registered
    handler. Handlers return either a dict (wrapped into a MagicMock with
    .to_dict()), a MagicMock (returned verbatim), or raise an exception
    (e.g. _FakeApiException(status=404, ...)).
    """

    def __init__(self):
        self._handlers = {}
        self._calls = []

    def on(self, method_name, response=None, raises=None):
        """Register a handler.

        - response: dict (auto-wrapped) or MagicMock (verbatim).
        - raises: exception instance to raise (overrides response).
        """
        if raises is not None:
            self._handlers[method_name] = ("raise", raises)
        elif isinstance(response, dict):
            self._handlers[method_name] = ("dict", response)
        else:
            self._handlers[method_name] = ("raw", response)

    @property
    def calls(self):
        """List of (method_name, body) recorded by the mock SDK client."""
        return list(self._calls)

    def _dispatch(self, method_name, body):
        self._calls.append((method_name, body))
        if method_name not in self._handlers:
            raise _FakeApiException(
                status=500,
                body=f"mock-server: no handler for {method_name!r}",
            )
        kind, payload = self._handlers[method_name]
        if kind == "raise":
            raise payload
        if kind == "dict":
            m = MagicMock(name=f"{method_name}_response")
            m.to_dict.return_value = payload
            return m
        return payload

    # ------------------------------------------------------------------
    # Top-level entry: load a module under test and run main() against
    # this mock server.
    # ------------------------------------------------------------------

    def run_module(self, module_filename, params, check_mode=False):
        """Load plugins/modules/<module_filename>, drive main() against
        this mock server, and return the SystemExit kwargs (from exit_json
        or fail_json)."""
        return _run_module_against_mock(self, module_filename, params, check_mode)


def _detect_collection_namespace():
    """Inspect a known module file to learn the runtime import path.

    The collection namespace is data-driven (currently drzln0.akeyless;
    set via `[platforms.ansible] galaxy_namespace` in provider.toml).
    Modules import the shared helper via the namespace they were generated
    against; we detect it from the first module file rather than hard-coding.
    """
    sample = MODULES_DIR / "role.py"
    source = sample.read_text()
    m = re.search(
        r"from ansible_collections\.([a-z0-9_]+)\.([a-z0-9_]+)\.plugins\.module_utils\.akeyless_client",
        source,
    )
    if not m:
        raise RuntimeError(
            "Could not detect collection namespace from role.py"
        )
    return m.group(1), m.group(2)


def _install_collection_helper(helper_module, namespace, name):
    """Stub the ansible_collections.<ns>.<name>.* tree pointing at the
    real akeyless_client helper."""
    parents = [
        "ansible_collections",
        f"ansible_collections.{namespace}",
        f"ansible_collections.{namespace}.{name}",
        f"ansible_collections.{namespace}.{name}.plugins",
        f"ansible_collections.{namespace}.{name}.plugins.module_utils",
    ]
    for n in parents:
        if n not in sys.modules:
            sys.modules[n] = types.ModuleType(n)
    full = (
        f"ansible_collections.{namespace}.{name}"
        ".plugins.module_utils.akeyless_client"
    )
    sys.modules[full] = helper_module


def _install_fake_akeyless(mock_client):
    """Insert a MagicMock-backed akeyless package whose V2Api(...) returns
    the supplied mock_client."""
    pkg = types.ModuleType("akeyless")
    pkg.__getattr__ = lambda name: MagicMock(name=f"akeyless.{name}")  # type: ignore[attr-defined]
    pkg.Configuration = MagicMock(name="akeyless.Configuration")
    pkg.ApiClient = MagicMock(name="akeyless.ApiClient")
    pkg.V2Api = MagicMock(name="akeyless.V2Api", return_value=mock_client)
    pkg.Auth = MagicMock(name="akeyless.Auth")
    exc = types.ModuleType("akeyless.exceptions")
    exc.ApiException = _FakeApiException
    pkg.exceptions = exc
    sys.modules["akeyless"] = pkg
    sys.modules["akeyless.exceptions"] = exc
    return pkg


def _install_fake_ansible_module(params, check_mode):
    """Install ansible.module_utils.basic.AnsibleModule as a factory that
    records params and raises SystemExit-with-kwargs on exit_json/fail_json."""
    ansible_mod = sys.modules.get("ansible") or types.ModuleType("ansible")
    util_mod = sys.modules.get("ansible.module_utils") or types.ModuleType("ansible.module_utils")
    basic_mod = types.ModuleType("ansible.module_utils.basic")
    sys.modules["ansible"] = ansible_mod
    sys.modules["ansible.module_utils"] = util_mod
    sys.modules["ansible.module_utils.basic"] = basic_mod
    ansible_mod.module_utils = util_mod
    util_mod.basic = basic_mod

    def factory(argument_spec=None, supports_check_mode=False, **_kw):
        module = MagicMock(name="AnsibleModule")
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

    basic_mod.AnsibleModule = factory  # type: ignore[attr-defined]
    return factory


def _load_helper():
    """Load plugins/module_utils/akeyless_client.py fresh."""
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_mock_helper", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_module(name):
    """Load plugins/modules/<name> fresh."""
    path = MODULES_DIR / name
    spec = importlib.util.spec_from_file_location(
        f"akeyless_mock_target_{path.stem}", path
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _run_module_against_mock(server, module_filename, params, check_mode):
    """Run a target module's main() against the mock server.

    Returns the kwargs dict from the SystemExit raised by exit_json /
    fail_json. The caller inspects this directly.
    """
    # Build the mock client: client.<method>(body) -> server._dispatch(...).
    client = MagicMock(name="MockV2ApiClient")

    def _make_caller(name):
        return lambda body: server._dispatch(name, body)

    # When a generated module calls e.g. client.create_role(body), route it
    # through the mock server's dispatch table.
    def __getattr__(name):  # noqa: N807
        return _make_caller(name)

    # MagicMock doesn't let us override __getattr__ on instances cleanly,
    # so wrap with a typed proxy.
    class _Proxy:
        def __init__(self):
            self._auth_resp = MagicMock()
            self._auth_resp.token = "mock-server-token"

        def auth(self, _body):
            return self._auth_resp

        def __getattr__(self, item):
            return _make_caller(item)

    proxy = _Proxy()

    namespace, name = _detect_collection_namespace()
    _install_fake_akeyless(proxy)
    helper = _load_helper()
    _install_collection_helper(helper, namespace, name)
    _install_fake_ansible_module(params or {}, check_mode)

    target = _load_module(module_filename)
    try:
        target.main()
    except SystemExit as e:
        return getattr(e, "kwargs", {}), getattr(e, "code", None)
    raise AssertionError(
        f"{module_filename}.main() returned without calling exit_json/fail_json"
    )


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_server():
    """Return a fresh MockServer per test (no cross-test contamination)."""
    saved = {
        k: sys.modules.get(k)
        for k in (
            "akeyless",
            "akeyless.exceptions",
            "ansible",
            "ansible.module_utils",
            "ansible.module_utils.basic",
        )
    }
    server = MockServer()
    try:
        yield server
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# Re-export the exception classes for tests that need to assert on
# ApiException-shaped raises (e.g. "what does the module do when GET returns
# 404?").
FakeApiException = _FakeApiException
ExitJsonCalled = _ExitJsonCalled
FailJsonCalled = _FailJsonCalled
