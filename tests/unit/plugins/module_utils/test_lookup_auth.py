# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/module_utils/akeyless_lookup_auth.py -- the
# shared authentication helper used by every lookup + inventory plugin.
# Previously these tests lived inside each lookup test file (since each
# lookup carried its own `_authenticated_client` function). After the
# DRY refactor that collapsed those into one helper, the per-lookup
# tests became redundant and live here instead.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"


# ---------------------------------------------------------------------------
# Stub setup
# ---------------------------------------------------------------------------


def _install_ansible_errors():
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleError"):
        class _AnsibleError(Exception):
            pass
        errors_mod.AnsibleError = _AnsibleError


def _make_fake_akeyless():
    """Build a fresh fake akeyless module (Configuration, V2Api,
    Auth, ApiClient, exceptions.ApiException). MagicMock-heavy so
    individual tests can wire in specific behaviour."""
    fake = types.ModuleType("akeyless")
    fake.Configuration = MagicMock(name="akeyless.Configuration")
    fake.ApiClient = MagicMock(name="akeyless.ApiClient")
    fake.V2Api = MagicMock(name="akeyless.V2Api")
    fake.Auth = MagicMock(name="akeyless.Auth")
    fake_exceptions = types.ModuleType("akeyless.exceptions")

    class _ApiException(Exception):
        def __init__(self, status=500, body="", reason=""):
            super().__init__(body or reason or "")
            self.status = status
            self.body = body
            self.reason = reason

    fake_exceptions.ApiException = _ApiException
    fake.exceptions = fake_exceptions
    return fake, fake_exceptions


def _load_helper(fake_akeyless, fake_exceptions):
    """Load akeyless_lookup_auth.py with the supplied fake akeyless
    SDK in sys.modules. Re-load each time so HAS_AKEYLESS captures
    the per-test fake."""
    _install_ansible_errors()
    sys.modules["akeyless"] = fake_akeyless
    sys.modules["akeyless.exceptions"] = fake_exceptions
    full = "akeyless_lookup_auth_under_test"
    sys.modules.pop(full, None)
    spec = importlib.util.spec_from_file_location(full, HELPER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def helper():
    fake, fake_exc = _make_fake_akeyless()
    return _load_helper(fake, fake_exc), fake, fake_exc


# ---------------------------------------------------------------------------
# Default constants
# ---------------------------------------------------------------------------


class TestDefaults:

    def test_default_gateway_url(self, helper):
        mod, _, _ = helper
        assert mod.DEFAULT_GATEWAY_URL == "https://api.akeyless.io"

    def test_default_access_type(self, helper):
        mod, _, _ = helper
        assert mod.DEFAULT_ACCESS_TYPE == "access_key"

    def test_has_akeyless_true_when_sdk_present(self, helper):
        mod, _, _ = helper
        assert mod.HAS_AKEYLESS is True
        assert mod.AKEYLESS_IMPORT_ERROR is None


# ---------------------------------------------------------------------------
# authenticated_client behaviour
# ---------------------------------------------------------------------------


class TestAuthenticatedClient:

    def test_pre_issued_token_skips_auth(self, helper):
        """When opts['token'] is set, authenticated_client must skip
        the auth() round-trip and return the verbatim token."""
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake.V2Api.return_value = fake_client
        client, token = mod.authenticated_client({"token": "pre-issued"})
        assert token == "pre-issued"
        assert client is fake_client
        assert not fake_client.auth.called

    def test_requires_access_id_when_no_token(self, helper):
        """No token + no access_id -> AnsibleError. Catches the
        common misconfiguration that would otherwise surface as a
        cryptic 401 from the gateway."""
        from ansible.errors import AnsibleError
        mod, _, _ = helper
        with pytest.raises(AnsibleError, match="access_id is required"):
            mod.authenticated_client({"token": None, "access_id": None})

    def test_runs_auth_when_access_id_supplied(self, helper):
        """With access_id but no token, authenticated_client calls
        client.auth(Auth(...)) and returns the response token."""
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="resolved-token")
        fake.V2Api.return_value = fake_client

        _, token = mod.authenticated_client({
            "access_id": "p-xxx",
            "access_key": "secret==",
        })
        assert token == "resolved-token"
        fake_client.auth.assert_called_once()

    def test_uses_gateway_url_from_opts(self, helper):
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="tok")
        fake.V2Api.return_value = fake_client

        mod.authenticated_client({
            "gateway_url": "https://my-gw.example.com",
            "access_id": "p-xxx",
            "access_key": "k",
        })
        fake.Configuration.assert_called_with(host="https://my-gw.example.com")

    def test_falls_back_to_default_gateway_url(self, helper):
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="tok")
        fake.V2Api.return_value = fake_client

        mod.authenticated_client({
            "access_id": "p-xxx",
            "access_key": "k",
        })
        fake.Configuration.assert_called_with(host="https://api.akeyless.io")

    def test_falls_back_to_default_access_type(self, helper):
        """access_type defaults to access_key (matches the historical
        Akeyless CLI default)."""
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="tok")
        fake.V2Api.return_value = fake_client

        mod.authenticated_client({
            "access_id": "p-xxx",
            "access_key": "k",
        })
        fake.Auth.assert_called_once()
        call_kwargs = fake.Auth.call_args.kwargs
        assert call_kwargs["access_type"] == "access_key"

    def test_api_exception_translated_to_ansible_error(self, helper):
        from ansible.errors import AnsibleError
        mod, fake, fake_exc = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.side_effect = fake_exc.ApiException(
            status=401, body="bad-creds"
        )
        fake.V2Api.return_value = fake_client

        with pytest.raises(AnsibleError, match=r"Akeyless auth failed.*401.*bad-creds"):
            mod.authenticated_client({
                "access_id": "p-xxx",
                "access_key": "wrong",
            })

    def test_empty_token_response_raises(self, helper):
        from ansible.errors import AnsibleError
        mod, fake, _ = helper
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token=None)
        fake.V2Api.return_value = fake_client

        with pytest.raises(AnsibleError, match="returned no token"):
            mod.authenticated_client({
                "access_id": "p-xxx",
                "access_key": "k",
            })
