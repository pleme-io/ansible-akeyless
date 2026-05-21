"""Smoke + behaviour tests for the `secret` lookup plugin.

Uses the same mocked-akeyless fixture pattern as the module tests so the
suite stays runnable without the SDK installed locally.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[4]
LOOKUP_PATH = ROOT / "plugins" / "lookup" / "secret.py"


@pytest.fixture
def fake_akeyless(monkeypatch):
    fake = MagicMock()
    fake.exceptions = MagicMock()

    class ApiException(Exception):
        def __init__(self, status=None, body=None, reason=None):
            super().__init__(body or reason or "ApiException")
            self.status = status
            self.body = body
            self.reason = reason

    fake.exceptions.ApiException = ApiException
    monkeypatch.setitem(sys.modules, "akeyless", fake)
    monkeypatch.setitem(sys.modules, "akeyless.exceptions", fake.exceptions)
    return fake


def _load_lookup_module():
    spec = importlib.util.spec_from_file_location("akeyless_secret_lookup", LOOKUP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


class _FakeLookupBase:
    """Minimal LookupBase substitute so the plugin loads without ansible."""

    def __init__(self):
        self._opts = {}

    def set_options(self, var_options=None, direct=None):
        if direct:
            self._opts.update(direct)

    def get_option(self, key):
        return self._opts.get(key)


def test_lookup_module_ast_parses():
    """The lookup plugin file must be syntactically valid Python."""
    import ast
    ast.parse(LOOKUP_PATH.read_text())


def test_lookup_module_declares_documentation():
    src = LOOKUP_PATH.read_text()
    assert 'DOCUMENTATION = ' in src
    assert "name: secret" in src
    assert "_terms:" in src
    assert "akeyless >= 5.0.22" in src


def test_lookup_module_returns_secret_values(fake_akeyless, monkeypatch):
    """Happy path: token + one call returns the requested secrets in order."""
    # Stub the akeyless SDK responses.
    fake_akeyless.Configuration.return_value = "config"
    fake_akeyless.ApiClient.return_value = "api_client"
    fake_client = MagicMock()
    fake_akeyless.V2Api.return_value = fake_client

    auth_res = MagicMock()
    auth_res.token = "stub-token"
    fake_client.auth.return_value = auth_res

    # Akeyless returns a dict {name: value}; the plugin reorders.
    response = MagicMock()
    response.to_dict.return_value = {
        "/svc/a": "value-a",
        "/svc/b": "value-b",
    }
    fake_client.get_secret_value.return_value = response

    # Patch ansible.plugins.lookup.LookupBase before loading the plugin.
    fake_ansible_lookup = MagicMock()
    fake_ansible_lookup.LookupBase = _FakeLookupBase
    fake_ansible_errors = MagicMock()
    fake_ansible_errors.AnsibleError = type("AnsibleError", (Exception,), {})
    fake_ansible_errors.AnsibleLookupError = type("AnsibleLookupError", (Exception,), {})
    monkeypatch.setitem(sys.modules, "ansible", MagicMock())
    monkeypatch.setitem(sys.modules, "ansible.errors", fake_ansible_errors)
    monkeypatch.setitem(sys.modules, "ansible.plugins", MagicMock())
    monkeypatch.setitem(sys.modules, "ansible.plugins.lookup", fake_ansible_lookup)

    mod = _load_lookup_module()
    lookup = mod.LookupModule()
    result = lookup.run(
        ["/svc/a", "/svc/b"],
        variables={},
        access_id="p-test",
        access_key="ak-test",
        access_type="access_key",
    )

    assert result == ["value-a", "value-b"]
    fake_client.auth.assert_called_once()
    fake_client.get_secret_value.assert_called_once()


def test_lookup_module_uses_pre_issued_token_when_present(fake_akeyless, monkeypatch):
    """If `token=` is set, the plugin must NOT call client.auth()."""
    fake_client = MagicMock()
    fake_akeyless.V2Api.return_value = fake_client

    response = MagicMock()
    response.to_dict.return_value = {"/svc/a": "value-a"}
    fake_client.get_secret_value.return_value = response

    fake_ansible_lookup = MagicMock()
    fake_ansible_lookup.LookupBase = _FakeLookupBase
    fake_ansible_errors = MagicMock()
    fake_ansible_errors.AnsibleError = type("AnsibleError", (Exception,), {})
    fake_ansible_errors.AnsibleLookupError = type("AnsibleLookupError", (Exception,), {})
    monkeypatch.setitem(sys.modules, "ansible", MagicMock())
    monkeypatch.setitem(sys.modules, "ansible.errors", fake_ansible_errors)
    monkeypatch.setitem(sys.modules, "ansible.plugins", MagicMock())
    monkeypatch.setitem(sys.modules, "ansible.plugins.lookup", fake_ansible_lookup)

    mod = _load_lookup_module()
    lookup = mod.LookupModule()
    result = lookup.run(
        ["/svc/a"],
        variables={},
        token="pre-issued-token",
    )

    assert result == ["value-a"]
    fake_client.auth.assert_not_called()
