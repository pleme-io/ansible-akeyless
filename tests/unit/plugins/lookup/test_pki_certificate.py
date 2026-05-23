# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/lookup/pki_certificate.py -- issues certs
# from Akeyless PKI cert issuers.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "pki_certificate.py"


def _install_ansible_lookup_stubs():
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleError"):
        class _E(Exception):
            pass
        errors_mod.AnsibleError = _E
    if not hasattr(errors_mod, "AnsibleLookupError"):
        class _L(Exception):
            pass
        errors_mod.AnsibleLookupError = _L

    if "ansible.plugins.lookup" not in sys.modules:
        plugins_mod = types.ModuleType("ansible.plugins")
        lookup_mod = types.ModuleType("ansible.plugins.lookup")

        class _StubLookupBase:
            def __init__(self):
                self._opts: dict = {}

            def set_options(self, var_options=None, direct=None):
                self._opts = dict(direct or {})
                for k, v in (var_options or {}).items():
                    self._opts.setdefault(k, v)

            def get_option(self, name):
                return self._opts.get(name)

        lookup_mod.LookupBase = _StubLookupBase
        sys.modules["ansible.plugins"] = plugins_mod
        sys.modules["ansible.plugins.lookup"] = lookup_mod
        ansible_pkg.plugins = plugins_mod


def _load(fake_akeyless):
    _install_ansible_lookup_stubs()
    fake_mod, _ = fake_akeyless
    fake_mod.GetPKICertificate = MagicMock(name="akeyless.GetPKICertificate")
    spec = importlib.util.spec_from_file_location(
        "akeyless_pki_cert_under_test", LOOKUP_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_pki_cert_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lookup(fake_akeyless):
    return _load(fake_akeyless)


# ---------------------------------------------------------------------------
# Module surface + auth
# ---------------------------------------------------------------------------


def test_lookup_module_class_exists(lookup):
    assert hasattr(lookup, "LookupModule")
    from ansible.plugins.lookup import LookupBase
    assert issubclass(lookup.LookupModule, LookupBase)


def test_pre_issued_token_skips_auth(lookup):
    client, token = lookup._authenticated_client({"token": "pre"})
    assert token == "pre"
    assert not client.auth.called


# ---------------------------------------------------------------------------
# Cert issue dispatch
# ---------------------------------------------------------------------------


def _wire_client(lookup, cert_response):
    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="tok")
    response = MagicMock()
    response.to_dict.return_value = cert_response
    fake_client.get_pki_certificate.return_value = response
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)
    return fake_client


class TestRun:

    def test_returns_cert_dict_per_term(self, lookup):
        _wire_client(lookup, {
            "cert": "-----BEGIN CERTIFICATE-----\nCC\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nKK\n-----END RSA PRIVATE KEY-----",
            "ca_chain": [],
        })
        inst = lookup.LookupModule()
        out = inst.run(
            ["/pki/server"],
            variables={},
            access_id="p-xxx", access_key="k",
            common_name="nginx.local",
        )
        assert len(out) == 1
        assert "cert" in out[0]
        assert "private_key" in out[0]

    def test_forwards_optional_args_to_body(self, lookup):
        """common_name / alt_names / ttl / key_data_base64 must all
        forward to the GetPKICertificate constructor."""
        fake_client = _wire_client(lookup, {})
        inst = lookup.LookupModule()
        inst.run(
            ["/pki/x"],
            variables={},
            access_id="p-xxx", access_key="k",
            common_name="svc.cluster.local",
            alt_names="svc,svc-headless",
            ttl=3600,
        )
        # The GetPKICertificate stub captured the kwargs.
        fake_client.get_pki_certificate.assert_called_once()
        # akeyless.GetPKICertificate was called with our kwargs.
        gpki_call = lookup.akeyless.GetPKICertificate.call_args
        assert gpki_call is not None
        kwargs = gpki_call.kwargs
        assert kwargs.get("common_name") == "svc.cluster.local"
        assert kwargs.get("alt_names") == "svc,svc-headless"
        assert kwargs.get("ttl") == 3600
        assert kwargs.get("cert_issuer_name") == "/pki/x"

    def test_empty_optional_args_are_dropped(self, lookup):
        """Optional args that are None or empty string don't get
        forwarded -- avoids upstream Akeyless rejecting an empty CN."""
        _wire_client(lookup, {})
        inst = lookup.LookupModule()
        inst.run(
            ["/pki/x"],
            variables={},
            access_id="p-xxx", access_key="k",
            common_name="",  # explicitly empty
            alt_names=None,
        )
        gpki_call = lookup.akeyless.GetPKICertificate.call_args
        kwargs = gpki_call.kwargs
        assert "common_name" not in kwargs
        assert "alt_names" not in kwargs

    def test_api_exception_raises_lookup_error(self, lookup):
        from akeyless.exceptions import ApiException
        from ansible.errors import AnsibleLookupError

        fake_client = MagicMock()
        fake_client.auth.return_value = MagicMock(token="tok")
        fake_client.get_pki_certificate.side_effect = ApiException(
            status=400, body="bad common_name"
        )
        lookup.akeyless.V2Api = MagicMock(return_value=fake_client)

        inst = lookup.LookupModule()
        with pytest.raises(AnsibleLookupError, match="400"):
            inst.run(["/pki/x"], variables={},
                     access_id="p-xxx", access_key="k")
