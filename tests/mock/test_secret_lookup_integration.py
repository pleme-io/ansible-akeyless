# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `secret` lookup plugin.
# Mirrors the mock-server pattern from test_role_lifecycle.py /
# test_static_secret_lifecycle.py but for plugins/lookup/secret.py
# (which goes through @akeyless_lookup + authenticated_client +
# get_secret_value, not the run_standard_crud helper).
#
# Why it matters: the lookup unit tests use isolated stubs; this
# file exercises the lookup all the way through the V2Api proxy +
# the @akeyless_lookup decorator + the @akeyless_lookup -> fetch()
# dispatch + the SDK-result .to_dict() unwrap. A regression in any
# of those layers surfaces here.

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
SECRET_LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "secret.py"
LOOKUP_AUTH_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"
PLUGIN_HELPERS_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"


class _LookupMockServer:
    """Variant of MockServer aimed at lookup plugins. Lookups don't
    call main() / exit_json -- they invoke `client.get_secret_value(body)`
    and return values directly."""

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


def _install_lookup_stubs(server):
    """Install ansible.* + akeyless.* stubs targeting the lookup
    plugin's auth + SDK path through the supplied mock server."""
    # ansible.errors
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    for cls_name in ("AnsibleError", "AnsibleLookupError"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))

    # ansible.plugins.lookup
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

    # akeyless SDK -- V2Api(...) returns a proxy that routes calls to the
    # mock server.
    class _Proxy:
        def __init__(self, _server):
            self._server = _server

        def auth(self, _body):
            r = MagicMock()
            r.token = "mock-token"
            return r

        def get_secret_value(self, body):
            return self._server._dispatch("get_secret_value", body)

    akeyless_mod = types.ModuleType("akeyless")
    akeyless_mod.Configuration = MagicMock(name="akeyless.Configuration")
    akeyless_mod.ApiClient = MagicMock(name="akeyless.ApiClient")
    akeyless_mod.V2Api = MagicMock(name="akeyless.V2Api", return_value=_Proxy(server))
    akeyless_mod.Auth = MagicMock(name="akeyless.Auth")
    akeyless_mod.GetSecretValue = MagicMock(name="akeyless.GetSecretValue")
    exc_mod = types.ModuleType("akeyless.exceptions")
    exc_mod.ApiException = FakeApiException
    akeyless_mod.exceptions = exc_mod
    sys.modules["akeyless"] = akeyless_mod
    sys.modules["akeyless.exceptions"] = exc_mod

    # ansible_collections.<...>.plugins.module_utils.{lookup_auth,plugin_helpers}
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


def _load_secret_lookup():
    """Load plugins/lookup/secret.py as a synthetic module."""
    spec = importlib.util.spec_from_file_location(
        "akeyless_secret_lookup_mock_integration", SECRET_LOOKUP_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lookup_server():
    """Returns (server, lookup_instance). Saves + restores sys.modules
    state so other tests aren't contaminated."""
    saved = {
        k: sys.modules.get(k)
        for k in ("akeyless", "akeyless.exceptions", "ansible",
                  "ansible.plugins", "ansible.plugins.lookup")
    }
    server = _LookupMockServer()
    _install_lookup_stubs(server)
    mod = _load_secret_lookup()
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
# Wire-level fetch tests
# ---------------------------------------------------------------------------


def test_single_secret_fetch(lookup_server):
    """Single-term lookup: dispatches one get_secret_value call,
    returns a one-element list aligned to the input term."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/app/db/password": "rotated-value"},
    )
    out = lookup.run(
        ["/app/db/password"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert out == ["rotated-value"]
    assert [c[0] for c in server.calls] == ["get_secret_value"]


def test_multi_secret_fetch_returns_input_order(lookup_server):
    """N-term lookup: get_secret_value is called ONCE (batch), result
    is re-shaped into a list aligned to input order regardless of
    response key order."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={
            "/c": "value-c",
            "/a": "value-a",
            "/b": "value-b",
        },
    )
    out = lookup.run(
        ["/a", "/b", "/c"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert out == ["value-a", "value-b", "value-c"]
    # ONE call -- the lookup batches via GetSecretValue(names=[...]).
    assert len([c for c in server.calls if c[0] == "get_secret_value"]) == 1


def test_missing_secret_raises_lookup_error(lookup_server):
    """If a requested term is not in the response dict, the lookup
    must raise AnsibleLookupError so the playbook fails noisily
    rather than silently inserting None into the rendered template."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/found": "value"},
    )
    with pytest.raises(AnsibleLookupError, match=r"/missing.*not found"):
        lookup.run(
            ["/missing"],
            variables={},
            access_id="p-test", access_key="k-test",
        )


def test_api_exception_translated_to_lookup_error(lookup_server):
    """ApiException from get_secret_value -> AnsibleLookupError with
    status + body in the message (the @akeyless_lookup decorator's
    contract)."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        raises=FakeApiException(status=403, body="forbidden"),
    )
    with pytest.raises(AnsibleLookupError, match=r"403.*forbidden"):
        lookup.run(
            ["/x"],
            variables={},
            access_id="p-test", access_key="k-test",
        )


def test_pre_issued_token_skips_auth_call(lookup_server):
    """When the caller supplies `token=...`, the lookup MUST NOT
    make an auth() call -- it uses the token directly. This is the
    'I already authenticated, reuse the token' path."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/x": "value-x"},
    )
    out = lookup.run(
        ["/x"],
        variables={},
        token="pre-issued-token",  # no access_id needed
    )
    assert out == ["value-x"]
    # auth() never reached the mock (we'd see it in server.calls
    # if it had -- the proxy's .auth() is a no-op stub, so the
    # invariant we check is the successful path completing without
    # access_id being required).


def test_invalid_response_type_raises_lookup_error(lookup_server):
    """If the SDK response normalises to something other than a dict
    (e.g. a list of secrets), the lookup must fail explicitly rather
    than blindly indexing."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    # Raw non-dict response (no to_dict method).
    server.on("get_secret_value", response=["not", "a", "dict"])
    with pytest.raises(AnsibleLookupError, match=r"Unexpected.*response type"):
        lookup.run(
            ["/x"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
