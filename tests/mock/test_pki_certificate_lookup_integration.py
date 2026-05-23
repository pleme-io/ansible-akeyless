# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `pki_certificate` lookup
# plugin. Like dynamic_secret, this is a per-term lookup, but it
# additionally exercises the extra_opts path of @akeyless_lookup
# (common_name, alt_names, ttl, key_data_base64 are surfaced via
# compact_kwargs into the GetPKICertificate body).

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
LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "pki_certificate.py"
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

    captured_body_kwargs = {}

    class _MockGetPKICertificate:
        """Capture the kwargs the lookup passes so tests can assert
        that compact_kwargs is dropping None/empty correctly."""

        def __init__(self, **kwargs):
            captured_body_kwargs.clear()
            captured_body_kwargs.update(kwargs)

    class _Proxy:
        def __init__(self, _server):
            self._server = _server
        def auth(self, _body):
            r = MagicMock()
            r.token = "mock-token"
            return r
        def get_pki_certificate(self, body):
            return self._server._dispatch("get_pki_certificate", body)

    akeyless_mod = types.ModuleType("akeyless")
    akeyless_mod.Configuration = MagicMock()
    akeyless_mod.ApiClient = MagicMock()
    akeyless_mod.V2Api = MagicMock(return_value=_Proxy(server))
    akeyless_mod.Auth = MagicMock()
    akeyless_mod.GetPKICertificate = _MockGetPKICertificate
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

    return captured_body_kwargs


def _load_lookup():
    spec = importlib.util.spec_from_file_location(
        "akeyless_pki_certificate_lookup_mock_integration", LOOKUP_PATH
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
    captured = _install_stubs(server)
    mod = _load_lookup()
    instance = mod.LookupModule()
    try:
        yield server, instance, captured
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# ---------------------------------------------------------------------------
# Cert issuance + extra_opts propagation
# ---------------------------------------------------------------------------


def test_issue_with_minimum_args(lookup_server):
    """Single issuer name, no CN/SAN/TTL -- the body must carry only
    the cert_issuer_name + token (not None/empty extras)."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={
            "cert": "-----BEGIN CERTIFICATE-----\nA\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nK\n-----END RSA PRIVATE KEY-----",
        },
    )
    out = lookup.run(
        ["/pki/server-issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 1
    assert "cert" in out[0]
    assert "private_key" in out[0]
    # Body should carry name + token, no spurious None entries.
    assert captured["cert_issuer_name"] == "/pki/server-issuer"
    assert captured["token"] == "mock-token"
    assert "common_name" not in captured
    assert "alt_names" not in captured


def test_extra_opts_propagated_to_body(lookup_server):
    """When common_name + alt_names + ttl are supplied, they must
    flow through compact_kwargs into the GetPKICertificate body."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM", "private_key": "KEY"},
    )
    lookup.run(
        ["/pki/server-issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
        common_name="web.example.com",
        alt_names="web,svc",
        ttl=3600,
    )
    assert captured["common_name"] == "web.example.com"
    assert captured["alt_names"] == "web,svc"
    assert captured["ttl"] == 3600


def test_empty_string_extras_dropped(lookup_server):
    """compact_kwargs drops empty strings -- a caller passing
    common_name='' should NOT cause the body to ship an empty
    CN field (Akeyless might reject)."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM"},
    )
    lookup.run(
        ["/pki/issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
        common_name="",       # should be dropped
        alt_names="real-san",  # should pass through
        ttl=None,             # should be dropped
    )
    assert "common_name" not in captured
    assert captured["alt_names"] == "real-san"
    assert "ttl" not in captured


def test_per_term_loop_for_multiple_issuers(lookup_server):
    """Each issuer term triggers one get_pki_certificate call."""
    server, lookup, _captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM"},
    )
    out = lookup.run(
        ["/pki/a", "/pki/b"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 2
    assert len([c for c in server.calls if c[0] == "get_pki_certificate"]) == 2


def test_api_exception_includes_issuer_name(lookup_server):
    """ApiException must surface the failing issuer name."""
    from ansible.errors import AnsibleLookupError
    server, lookup, _captured = lookup_server
    server.on(
        "get_pki_certificate",
        raises=FakeApiException(status=403, body="forbidden"),
    )
    with pytest.raises(AnsibleLookupError, match=r"unauthorized-issuer.*403"):
        lookup.run(
            ["/pki/unauthorized-issuer"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
