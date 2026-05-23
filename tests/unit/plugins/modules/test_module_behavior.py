# Copyright: (c) 2026, pleme-io
# MIT License
#
# Behaviour tests for one representative module per category.
#
# Each test installs `akeyless` + `akeyless.exceptions` + the
# `ansible.module_utils.basic.AnsibleModule` factory as mocks, then
# imports the target module fresh and drives main(). Outcomes are
# observed via the exit_json / fail_json call payloads.
#
# We don't try to exhaustively test every module -- that's what the
# generator snapshot tests cover. We test one of each shape:
#   * role.py             - CRUD with all four operations
#   * role_info.py        - data source (read-only)
#   * uid_generate_token  - action with sensitive_response_fields

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import functools
import importlib.util
import inspect
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


def _install_collection_helper(helper_module):
    """Bind the loaded helper module under the
    `ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client`
    path so generated modules' `from ansible_collections...` import resolves."""
    parents = [
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ]
    for name in parents:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)
    full = (
        "ansible_collections.drzln0.akeyless"
        ".plugins.module_utils.akeyless_client"
    )
    sys.modules[full] = helper_module


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_behavior_helper", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_module(name):
    path = MODULES_DIR / name
    spec = importlib.util.spec_from_file_location(
        f"akeyless_target_module_{path.stem}", path
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


@pytest.fixture
def harness(fake_akeyless, fake_ansible_module):
    """Set up fakes and a freshly loaded module under test.

    Returns a builder `build(name, params, check_mode=False)` that loads
    the named module and returns (module_under_test, ansible_mock,
    sdk_v2api_mock).
    """
    fake_akeyless_mod, _exc = fake_akeyless
    helper_mod = _load_helper()
    _install_collection_helper(helper_mod)

    def build(name, params=None, check_mode=False, v2api_mock=None):
        # AnsibleModule factory that records params into module.params.
        factory = fake_ansible_module(params=params or {}, check_mode=check_mode)
        # The akeyless package's V2Api should return this client on call.
        client_mock = v2api_mock if v2api_mock is not None else MagicMock(name="V2Api()")
        # When the generated module calls get_client, get_client invokes
        # akeyless.V2Api(akeyless.ApiClient(...)) -- so V2Api(...) → client.
        fake_akeyless_mod.V2Api = MagicMock(name="V2Api", return_value=client_mock)
        # auth() must return an obj with .token.
        auth_resp = MagicMock()
        auth_resp.token = "test-token"
        client_mock.auth.return_value = auth_resp

        target = _load_module(name)
        # Force the target module's `call_api`/`build_body`/`get_client`
        # references to come from our freshly loaded helper (it was already
        # imported by the target via the ansible_collections path).
        return target, factory, client_mock

    return build


def _result_mock(d):
    """Return a MagicMock whose to_dict() returns d."""
    m = MagicMock()
    m.to_dict.return_value = d
    return m


def module_test(name, params=None, check_mode=False):
    """Decorator: drop the 3-line harness boilerplate from every test.

    Usage:
        @module_test("role.py", params={"name": "r1", "access_id": "p", ...})
        def test_role_create_calls_sdk(target, client):
            client.get_role.side_effect = ApiException(status=404, body="missing")
            ...

    Pytest-friendly: the decorator rewrites the wrapped function's
    signature so pytest's fixture discovery still sees `harness` (and
    any other fixtures the inner function asked for, like `monkeypatch`).
    The inner function only declares `target, client, *other_fixtures`;
    the harness call + factory unpacking happens once, in the wrapper.
    """
    bind_params = params or {}

    def decorator(fn):
        sig = inspect.signature(fn)
        # Strip target/client from the visible signature (the wrapper
        # injects them); keep every other fixture parameter so pytest
        # can still inject e.g. monkeypatch, tmp_path, etc.
        passthrough = [
            p for n, p in sig.parameters.items()
            if n not in ("target", "client")
        ]

        @functools.wraps(fn)
        def wrapper(harness, **kwargs):
            target, _factory, client = harness(
                name, params=bind_params, check_mode=check_mode,
            )
            return fn(target=target, client=client, **kwargs)

        new_sig_params = [
            inspect.Parameter("harness", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ] + passthrough
        wrapper.__signature__ = inspect.Signature(new_sig_params)
        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# CRUD: role.py
# ---------------------------------------------------------------------------


@module_test(
    "role.py",
    params={"name": "r1", "access_id": "p", "access_key": "k", "state": "present"},
)
def test_role_create_calls_sdk(target, client, monkeypatch):
    monkeypatch.setenv("AKEYLESS_TOKEN", "")  # ensure auth path runs

    # read returns None -> create branch
    from akeyless.exceptions import ApiException

    client.get_role.side_effect = ApiException(status=404, body="missing")
    client.create_role.return_value = _result_mock({"created": True})

    with pytest.raises(SystemExit):
        target.main()
    client.create_role.assert_called_once()


@module_test(
    "role.py",
    params={
        "name": "r1",
        "access_id": "p",
        "access_key": "k",
        "state": "present",
        "description": "new-description",
    },
)
def test_role_update_when_exists_and_drift(target, client):
    """When the resource exists AND a desired param differs from
    current state, the module calls update_resource and reports
    changed=True with diff metadata. This is the post-idempotency
    contract -- pre-idempotency, update was unconditional."""
    # current has different description -> drift -> update called
    client.get_role.return_value = _result_mock(
        {"name": "r1", "description": "old-description"})
    client.update_role.return_value = _result_mock({"updated": True})

    with pytest.raises(SystemExit) as ei:
        target.main()
    client.update_role.assert_called_once()
    client.create_role.assert_not_called()
    assert ei.value.kwargs.get("changed") is True
    diff = ei.value.kwargs.get("diff")
    assert diff is not None, "drift path must emit diff metadata"
    assert diff["before"]["description"] == "old-description"
    assert diff["after"]["description"] == "new-description"


@module_test(
    "role.py",
    params={
        "name": "r1",
        "access_id": "p",
        "access_key": "k",
        "state": "present",
        "description": "matching-description",
    },
)
def test_role_no_update_when_in_desired_state(target, client):
    """Honest idempotency: when current state matches the desired
    params, the module skips the API write entirely and returns
    changed=False. The whole point of the compute_diff layer."""
    client.get_role.return_value = _result_mock(
        {"name": "r1", "description": "matching-description"})

    with pytest.raises(SystemExit) as ei:
        target.main()
    client.update_role.assert_not_called()
    client.create_role.assert_not_called()
    assert ei.value.kwargs.get("changed") is False
    assert "already in desired state" in (ei.value.kwargs.get("msg") or "")


@module_test(
    "role.py",
    params={"name": "r1", "access_id": "p", "access_key": "k", "state": "absent"},
)
def test_role_delete_when_exists(target, client):
    client.get_role.return_value = _result_mock({"name": "r1"})
    client.delete_role.return_value = _result_mock({"deleted": True})

    with pytest.raises(SystemExit) as ei:
        target.main()
    client.delete_role.assert_called_once()
    assert ei.value.kwargs.get("changed") is True


@module_test(
    "role.py",
    params={"name": "r1", "access_id": "p", "access_key": "k", "state": "absent"},
)
def test_role_delete_no_op_when_absent(target, client):
    from akeyless.exceptions import ApiException

    client.get_role.side_effect = ApiException(status=404, body="missing")

    with pytest.raises(SystemExit) as ei:
        target.main()
    client.delete_role.assert_not_called()
    assert ei.value.kwargs.get("changed") is False


@module_test(
    "role.py",
    params={"name": "r1", "access_id": "p", "access_key": "k", "state": "present"},
    check_mode=True,
)
def test_role_check_mode_short_circuits(target, client):
    # read returns a value (resource exists)
    client.get_role.return_value = _result_mock({"name": "r1"})

    with pytest.raises(SystemExit) as ei:
        target.main()
    # check_mode + state=present + current exists => changed=False (no diff)
    assert ei.value.kwargs.get("changed") is False
    client.create_role.assert_not_called()
    client.update_role.assert_not_called()
    client.delete_role.assert_not_called()


# ---------------------------------------------------------------------------
# Action: uid_generate_token.py (mutating, sensitive response fields)
# ---------------------------------------------------------------------------


@module_test(
    "uid_generate_token.py",
    params={
        "auth_method_name": "uid1",
        "access_id": "p",
        "access_key": "k",
    },
)
def test_uid_generate_token_returns_token_verbatim(target, client):
    """An earlier draft masked the token server-side, but chained tasks
    (uid_rotate_token / uid_create_child_token / uid_list_children) all
    need the cleartext value. Redaction has to live at the playbook
    layer via `no_log: true`, not in the module."""
    client.uid_generate_token.return_value = _result_mock(
        {"token": "real-secret", "uid_token": "uid-secret", "ttl": 60}
    )

    with pytest.raises(SystemExit) as ei:
        target.main()
    result = ei.value.kwargs.get("result")
    assert result["token"] == "real-secret"
    assert result["uid_token"] == "uid-secret"
    assert result["ttl"] == 60
    assert ei.value.kwargs.get("changed") is True


# ---------------------------------------------------------------------------
# Info: role_info.py
# ---------------------------------------------------------------------------


@module_test(
    "role_info.py",
    params={"name": "r1", "access_id": "p", "access_key": "k"},
)
def test_role_info_returns_data_dict(target, client):
    client.get_role.return_value = _result_mock({"name": "r1", "rules": []})

    with pytest.raises(SystemExit) as ei:
        target.main()
    assert ei.value.kwargs.get("changed") is False
    assert ei.value.kwargs.get("result") == {"name": "r1", "rules": []}


# ---------------------------------------------------------------------------
# call_api ApiException -> module.fail_json
# ---------------------------------------------------------------------------


@module_test(
    "role.py",
    params={"name": "r1", "access_id": "p", "access_key": "k", "state": "present"},
)
def test_call_api_failure_calls_fail_json(target, client):
    from akeyless.exceptions import ApiException

    # get_role raises a non-404 ApiException -> fail_json (status 500).
    client.get_role.side_effect = ApiException(status=500, body="boom")

    with pytest.raises(SystemExit) as ei:
        target.main()
    # _FailJsonCalled in conftest -> SystemExit(1) with kwargs.
    assert ei.value.kwargs.get("status") == 500
