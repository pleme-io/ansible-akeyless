# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `dynamic_secret` lookup plugin.
# Mirrors test_secret_lookup_integration.py but for the per-term
# (vs batch) shape -- dynamic_secret_get is a one-secret-per-call API,
# unlike GetSecretValue's batch.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from .conftest import FakeApiException

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "dynamic_secret.py"
LOOKUP_AUTH_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"
PLUGIN_HELPERS_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"


class _LookupMockServer:
    def __init__(self):
        self._handlers = {}
        self.calls = []

    def on(self, method_name, response=None, raises=None):
        if raises is not None:
            self._handlers[method_name] = ("raise", raises)
        elif isinstance(response, dict):
            self._handlers[method_name] = ("dict", response)
        else:
            self._handlers[method_name] = ("raw", response)

    def _dispatch(self, method_name, body):
        self.calls.append((method_name, body))
        if method_name not in self._handlers:
            raise FakeApiException(
                status=500, body=f"no handler for {method_name!r}",
            )
        kind, payload = self._handlers[method_name]
        if kind == "raise":
            raise payload
        if kind == "dict":
            m = MagicMock(name=f"{method_name}_response")
            m.to_dict.return_value = payload
            return m
        return payload


def _install_stubs(server):
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    for cls_name in ("AnsibleError", "AnsibleLookupError"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))

    plugins_pkg = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    lookup_mod = sys.modules.setdefault(
        "ansible.plugins.lookup", types.ModuleType("ansible.plugins.lookup")
    )
    plugins_pkg.lookup = lookup_mod
    ansible_pkg.plugins = plugins_pkg
    if not hasattr(lookup_mod, "LookupBase"):
        class _LookupBase:
            def __init__(self):
                self._opts: dict = {}
            def set_options(self, var_options=None, direct=None):
                self._opts = dict(direct or {})
                for k, v in (var_options or {}).items():
                    self._opts.setdefault(k, v)
            def get_option(self, name):
                return self._opts.get(name)
        lookup_mod.LookupBase = _LookupBase

    class _Proxy:
        def __init__(self, _server):
            self._server = _server
        def auth(self, _body):
            r = MagicMock()
            r.token = "mock-token"
            return r
        def get_dynamic_secret_value(self, body):
            return self._server._dispatch("get_dynamic_secret_value", body)

    akeyless_mod = types.ModuleType("akeyless")
    akeyless_mod.Configuration = MagicMock()
    akeyless_mod.ApiClient = MagicMock()
    akeyless_mod.V2Api = MagicMock(return_value=_Proxy(server))
    akeyless_mod.Auth = MagicMock()
    akeyless_mod.GetDynamicSecretValue = MagicMock()
    exc_mod = types.ModuleType("akeyless.exceptions")
    exc_mod.ApiException = FakeApiException
    akeyless_mod.exceptions = exc_mod
    sys.modules["akeyless"] = akeyless_mod
    sys.modules["akeyless.exceptions"] = exc_mod

    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))
    for stem, path in (
        ("akeyless_lookup_auth", LOOKUP_AUTH_PATH),
        ("akeyless_plugin_helpers", PLUGIN_HELPERS_PATH),
    ):
        full = f"ansible_collections.drzln0.akeyless.plugins.module_utils.{stem}"
        sys.modules.pop(full, None)
        spec = importlib.util.spec_from_file_location(full, path)
        m = importlib.util.module_from_spec(spec)
        sys.modules[full] = m
        spec.loader.exec_module(m)


def _load_lookup():
    spec = importlib.util.spec_from_file_location(
        "akeyless_dynamic_secret_lookup_mock_integration", LOOKUP_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lookup_server():
    saved = {
        k: sys.modules.get(k)
        for k in ("akeyless", "akeyless.exceptions", "ansible",
                  "ansible.plugins", "ansible.plugins.lookup")
    }
    server = _LookupMockServer()
    _install_stubs(server)
    mod = _load_lookup()
    instance = mod.LookupModule()
    try:
        yield server, instance
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# ---------------------------------------------------------------------------
# Per-term dispatch semantics
# ---------------------------------------------------------------------------


def test_single_term_one_call(lookup_server):
    """Single term -> single get_dynamic_secret_value call,
    response unwrapped to dict via to_dict()."""
    server, lookup = lookup_server
    server.on(
        "get_dynamic_secret_value",
        response={"user": "tmp_user", "password": "tmp_pass", "ttl": 1800},
    )
    out = lookup.run(
        ["/dynamic/db/readonly"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 1
    assert out[0]["user"] == "tmp_user"
    assert out[0]["password"] == "tmp_pass"
    assert len([c for c in server.calls if c[0] == "get_dynamic_secret_value"]) == 1


def test_multi_term_calls_per_term(lookup_server):
    """N terms -> N get_dynamic_secret_value calls (per-term mode,
    not batched). Result list aligned to input order."""
    server, lookup = lookup_server
    call_count = {"n": 0}
    responses = [
        {"user": "u_a", "password": "p_a"},
        {"user": "u_b", "password": "p_b"},
        {"user": "u_c", "password": "p_c"},
    ]

    def _per_call(name):
        idx = call_count["n"]
        call_count["n"] += 1
        return responses[idx]

    # Register a single handler that returns based on call count.
    server._handlers["get_dynamic_secret_value"] = (
        "callable", lambda body: _per_call(body),
    )
    # Patch the dispatch to support "callable" kind.
    orig_dispatch = server._dispatch

    def _new_dispatch(method_name, body):
        if method_name in server._handlers and server._handlers[method_name][0] == "callable":
            server.calls.append((method_name, body))
            payload = server._handlers[method_name][1](body)
            m = MagicMock()
            m.to_dict.return_value = payload
            return m
        return orig_dispatch(method_name, body)
    server._dispatch = _new_dispatch

    out = lookup.run(
        ["/a", "/b", "/c"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 3
    assert out[0]["user"] == "u_a"
    assert out[1]["user"] == "u_b"
    assert out[2]["user"] == "u_c"
    # 3 calls -- one per term.
    assert len([c for c in server.calls if c[0] == "get_dynamic_secret_value"]) == 3


def test_api_exception_per_term_translates_with_term_context(lookup_server):
    """ApiException on a specific term must surface the term name in
    the AnsibleLookupError -- otherwise the operator can't tell
    which dynamic secret broke when one of N requested fails."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_dynamic_secret_value",
        raises=FakeApiException(status=404, body="dynamic secret not found"),
    )
    with pytest.raises(AnsibleLookupError, match=r"missing.*404"):
        lookup.run(
            ["/dynamic/missing"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
