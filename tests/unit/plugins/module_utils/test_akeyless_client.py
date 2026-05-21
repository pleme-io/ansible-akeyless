# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/module_utils/akeyless_client.py.
#
# The helper file isn't a proper Python package (it ships under the
# ansible_collections path which only resolves inside a collection),
# so we load it via importlib.util with the akeyless SDK mocked
# beforehand.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class _Exit(SystemExit):
    """fail_json terminator -- the real AnsibleModule.fail_json calls sys.exit."""

    def __init__(self, **kwargs):
        super().__init__(1)
        self.kwargs = kwargs


def _mock_module():
    """A MagicMock module whose fail_json raises (mirrors real Ansible behaviour)."""
    module = MagicMock()
    module.fail_json.side_effect = lambda **kw: (_ for _ in ()).throw(_Exit(**kw))
    return module

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


def _load_helper(akeyless_mod):
    """Import the helper module fresh under a synthetic name.

    Each call returns a new module object so per-test state (HAS_AKEYLESS,
    module-level references) doesn't leak across tests.
    """
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_under_test", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    # Make sure imports inside the helper see our fake akeyless package.
    sys.modules["akeyless_client_under_test"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    # Sanity: helper picked up the SDK; tests that need a stub should
    # have installed it via the fake_akeyless fixture before calling us.
    return mod


@pytest.fixture
def helper(fake_akeyless):
    """Load the helper module with akeyless mocked."""
    return _load_helper(fake_akeyless[0])


# ---------------------------------------------------------------------------
# get_client
# ---------------------------------------------------------------------------


def test_get_client_uses_default_gateway_when_unset(monkeypatch, helper):
    monkeypatch.delenv("AKEYLESS_GATEWAY_URL", raising=False)
    monkeypatch.delenv("AKEYLESS_TOKEN", raising=False)
    monkeypatch.delenv("AKEYLESS_ACCESS_ID", raising=False)
    monkeypatch.delenv("AKEYLESS_ACCESS_KEY", raising=False)

    module = _mock_module()
    module.params = {"access_id": "p-1", "access_key": "k-1"}

    fake_akeyless = sys.modules["akeyless"]
    auth_result = MagicMock()
    auth_result.token = "t-from-auth"
    fake_akeyless.V2Api.return_value.auth.return_value = auth_result

    client, token = helper.get_client(module)
    assert token == "t-from-auth"
    # Configuration constructed with the default gateway URL.
    fake_akeyless.Configuration.assert_called_with(host=helper.DEFAULT_GATEWAY_URL)
    assert client is fake_akeyless.V2Api.return_value


def test_get_client_resolves_from_env(monkeypatch, helper):
    monkeypatch.setenv("AKEYLESS_GATEWAY_URL", "https://env.example/api")
    monkeypatch.setenv("AKEYLESS_ACCESS_ID", "p-env")
    monkeypatch.setenv("AKEYLESS_ACCESS_KEY", "k-env")
    monkeypatch.delenv("AKEYLESS_TOKEN", raising=False)

    module = _mock_module()
    module.params = {}

    fake_akeyless = sys.modules["akeyless"]
    auth_result = MagicMock()
    auth_result.token = "t-env"
    fake_akeyless.V2Api.return_value.auth.return_value = auth_result

    _client, token = helper.get_client(module)
    assert token == "t-env"
    fake_akeyless.Configuration.assert_called_with(host="https://env.example/api")


def test_get_client_pre_issued_token_short_circuits(monkeypatch, helper):
    monkeypatch.setenv("AKEYLESS_TOKEN", "pre-issued-tok")
    monkeypatch.delenv("AKEYLESS_ACCESS_ID", raising=False)

    module = _mock_module()
    module.params = {}

    fake_akeyless = sys.modules["akeyless"]
    _client, token = helper.get_client(module)
    assert token == "pre-issued-tok"
    # No auth() call performed when AKEYLESS_TOKEN is present.
    fake_akeyless.V2Api.return_value.auth.assert_not_called()


def test_get_client_fails_when_access_id_missing(monkeypatch, helper):
    monkeypatch.delenv("AKEYLESS_TOKEN", raising=False)
    monkeypatch.delenv("AKEYLESS_ACCESS_ID", raising=False)
    monkeypatch.delenv("AKEYLESS_ACCESS_KEY", raising=False)

    module = _mock_module()
    module.params = {}
    # Real fail_json terminates the process; our mock raises SystemExit.
    with pytest.raises(SystemExit):
        helper.get_client(module)
    args, kwargs = module.fail_json.call_args
    assert "access_id is required" in kwargs.get("msg", "")


# ---------------------------------------------------------------------------
# build_body
# ---------------------------------------------------------------------------


def test_build_body_filters_none_and_unknown(helper):
    fake_akeyless = sys.modules["akeyless"]

    class CreateRole:
        def __init__(self, name, description=None, token=None):
            self.name = name
            self.description = description
            self.token = token

    fake_akeyless.CreateRole = CreateRole

    body = helper.build_body(
        "CreateRole",
        {
            "name": "r1",
            "description": None,            # should be dropped (None)
            "unknown_field": "x",            # should be dropped (not accepted)
            "token": "tok",
        },
    )
    assert isinstance(body, CreateRole)
    assert body.name == "r1"
    assert body.description is None
    assert body.token == "tok"


def test_build_body_unknown_model_raises(helper):
    # The fake `akeyless` module returns MagicMock for any unknown attribute
    # (via __getattr__). To exercise the not-found branch in build_body,
    # explicitly set the attribute to None which takes precedence over
    # __getattr__ for normal lookup.
    fake_akeyless = sys.modules["akeyless"]
    fake_akeyless.NoSuchModel = None

    with pytest.raises(ValueError) as ei:
        helper.build_body("NoSuchModel", {})
    assert "Unknown Akeyless model" in str(ei.value)


# ---------------------------------------------------------------------------
# call_api
# ---------------------------------------------------------------------------


def test_call_api_invokes_method_and_to_dicts(helper):
    module = _mock_module()
    client = MagicMock()
    result_obj = MagicMock()
    result_obj.to_dict.return_value = {"id": "abc"}
    client.get_role.return_value = result_obj

    out = helper.call_api(module, client, "get_role", {"name": "r"})
    assert out == {"id": "abc"}
    client.get_role.assert_called_once_with({"name": "r"})


def test_call_api_fails_on_api_exception(helper):
    from akeyless.exceptions import ApiException

    module = _mock_module()
    client = MagicMock()
    client.create_role.side_effect = ApiException(status=500, body="boom", reason="x")

    with pytest.raises(SystemExit):
        helper.call_api(module, client, "create_role", {"name": "r"})
    args, kwargs = module.fail_json.call_args
    assert kwargs["status"] == 500
    assert "create_role" in kwargs["msg"]


def test_call_api_swallows_404_when_asked(helper):
    from akeyless.exceptions import ApiException

    module = _mock_module()
    client = MagicMock()
    client.get_role.side_effect = ApiException(status=404, body="missing", reason="nf")

    out = helper.call_api(module, client, "get_role", {"name": "r"}, swallow_404=True)
    assert out is None
    module.fail_json.assert_not_called()


def test_call_api_does_not_swallow_404_by_default(helper):
    from akeyless.exceptions import ApiException

    module = _mock_module()
    client = MagicMock()
    client.get_role.side_effect = ApiException(status=404, body="missing", reason="nf")

    with pytest.raises(SystemExit):
        helper.call_api(module, client, "get_role", {"name": "r"})
    module.fail_json.assert_called_once()


def test_call_api_unknown_method_fails(helper):
    module = _mock_module()
    client = MagicMock(spec=[])  # spec=[] makes any attribute access AttributeError

    with pytest.raises(SystemExit):
        helper.call_api(module, client, "does_not_exist", {})
    args, kwargs = module.fail_json.call_args
    assert "does_not_exist" in kwargs["msg"]


# ---------------------------------------------------------------------------
# _to_dict
# ---------------------------------------------------------------------------


def test_to_dict_handles_none(helper):
    assert helper._to_dict(None) is None


def test_to_dict_handles_dict_passthrough(helper):
    d = {"a": 1}
    assert helper._to_dict(d) is d


def test_to_dict_handles_object_with_to_dict(helper):
    obj = MagicMock()
    obj.to_dict.return_value = {"converted": True}
    assert helper._to_dict(obj) == {"converted": True}


def test_to_dict_wraps_scalar_result(helper):
    out = helper._to_dict("scalar")
    assert out == {"result": "scalar"}
