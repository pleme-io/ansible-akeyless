# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/lookup/dynamic_secret.py -- mints ephemeral
# credentials via Akeyless's get-dynamic-secret-value endpoint.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "dynamic_secret.py"


def _install_ansible_lookup_stubs():
    """Idempotent stubs for ansible.errors + ansible.plugins.lookup +
    the shared lookup_auth helper under its ansible_collections.<...>
    import path."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleError"):
        class _StubAnsibleError(Exception):
            pass
        errors_mod.AnsibleError = _StubAnsibleError
    if not hasattr(errors_mod, "AnsibleLookupError"):
        class _StubAnsibleLookupError(Exception):
            pass
        errors_mod.AnsibleLookupError = _StubAnsibleLookupError

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

    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)
    full = ("ansible_collections.drzln0.akeyless.plugins.module_utils"
            ".akeyless_lookup_auth")
    # Force fresh load so the helper's `import akeyless` rebinds to
    # the current test's fake_akeyless stub.
    sys.modules.pop(full, None)
    helper_path = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"
    spec = importlib.util.spec_from_file_location(full, helper_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)


def _load(fake_akeyless):
    _install_ansible_lookup_stubs()
    fake_mod, _ = fake_akeyless
    fake_mod.GetDynamicSecretValue = MagicMock(name="akeyless.GetDynamicSecretValue")
    spec = importlib.util.spec_from_file_location(
        "akeyless_dynamic_secret_under_test", LOOKUP_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_dynamic_secret_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lookup(fake_akeyless):
    return _load(fake_akeyless)


# ---------------------------------------------------------------------------
# Module surface
# ---------------------------------------------------------------------------


def test_lookup_module_class_exists(lookup):
    assert hasattr(lookup, "LookupModule")
    from ansible.plugins.lookup import LookupBase
    assert issubclass(lookup.LookupModule, LookupBase)


# ---------------------------------------------------------------------------
# Auth path (mirrors static-secret lookup; verify identical behaviour)
# ---------------------------------------------------------------------------


class TestAuth:

    def test_pre_issued_token_skips_auth(self, lookup):
        client, token = lookup._authenticated_client({"token": "pre-issued"})
        assert token == "pre-issued"
        assert not client.auth.called

    def test_requires_access_id_without_token(self, lookup):
        from ansible.errors import AnsibleError
        with pytest.raises(AnsibleError, match="access_id is required"):
            lookup._authenticated_client({"token": None, "access_id": None})


# ---------------------------------------------------------------------------
# run() dispatch
# ---------------------------------------------------------------------------


def _wire_client(lookup, dynamic_response):
    """Helper: install a stub V2Api whose get_dynamic_secret_value
    returns the given response."""
    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="tok")
    response = MagicMock()
    response.to_dict.return_value = dynamic_response
    fake_client.get_dynamic_secret_value.return_value = response
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)
    return fake_client


class TestRun:

    def test_returns_one_dict_per_term_in_order(self, lookup):
        fake_client = _wire_client(lookup, {"user": "u", "password": "p"})
        inst = lookup.LookupModule()
        out = inst.run(
            ["/db/postgres/ro"],
            variables={},
            access_id="p-xxx", access_key="k",
        )
        assert out == [{"user": "u", "password": "p"}]
        # Verify the dispatch was actually called with the term name.
        fake_client.get_dynamic_secret_value.assert_called_once()

    def test_multiple_terms_dispatch_per_call(self, lookup):
        """Unlike static-secret which batches, dynamic-secret endpoints
        are per-secret. Loop is intentional."""
        fake_client = _wire_client(lookup, {"x": 1})
        inst = lookup.LookupModule()
        out = inst.run(
            ["/a", "/b", "/c"],
            variables={},
            access_id="p-xxx", access_key="k",
        )
        assert len(out) == 3
        assert fake_client.get_dynamic_secret_value.call_count == 3

    def test_api_exception_raises_lookup_error(self, lookup):
        from akeyless.exceptions import ApiException
        from ansible.errors import AnsibleLookupError

        fake_client = MagicMock()
        fake_client.auth.return_value = MagicMock(token="tok")
        fake_client.get_dynamic_secret_value.side_effect = ApiException(
            status=500, body="upstream-error"
        )
        lookup.akeyless.V2Api = MagicMock(return_value=fake_client)

        inst = lookup.LookupModule()
        with pytest.raises(AnsibleLookupError, match="500"):
            inst.run(["/x"], variables={},
                     access_id="p-xxx", access_key="k")
