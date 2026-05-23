# Copyright: (c) 2026, pleme-io
# MIT License
#
# Behavioral tests for the three collapsed-shape lifecycle helpers in
# plugins/module_utils/akeyless_client.py:
#
#   * run_info_module      — *_info data-source modules
#   * run_action_module    — one-shot action modules (sign/encrypt/...)
#   * run_standard_crud    — full CRUD lifecycle modules
#
# 208/208 modules in plugins/modules/*.py route through one of these,
# so any regression here breaks the entire collection. These tests
# pin the contract: which SDK methods get called, what changed= /
# diff= payload is emitted, how check_mode is honored, and how the
# `immutable` + `idempotent` flags behave.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_lifecycle_under_test", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_client_lifecycle_under_test"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


@pytest.fixture
def helper(fake_akeyless):
    return _load_helper()


# ---------------------------------------------------------------------------
# Test driver
# ---------------------------------------------------------------------------

# Each test stubs out the three primitives (`get_client`, `build_body`,
# `call_api`) on the loaded helper module so we can assert exactly what
# gets dispatched without invoking the SDK. Returning a recording stub
# lets each test assert on `.invocations`.


class _Recorder:
    """Records call_api invocations and returns scripted responses by method."""

    def __init__(self, responses_by_method=None):
        # method_name -> response (will be returned on next call to that method)
        self.responses = dict(responses_by_method or {})
        self.invocations = []  # list of (method, body, swallow_404)

    def __call__(self, module, client, method, body, swallow_404=False):
        self.invocations.append((method, body, swallow_404))
        return self.responses.get(method)


def _drive(helper, params, *, fake_ansible_module, check_mode=False,
           call_responses=None):
    """Wire up the helper with AnsibleModule stub + primitive recorders.

    Returns the (recorder, raised_exit_kwargs) tuple. raised_exit_kwargs
    is the kwargs dict from whichever exit_json / fail_json terminated
    the helper.
    """
    factory = fake_ansible_module(params=params, check_mode=check_mode)
    recorder = _Recorder(call_responses or {})
    # Patch helper primitives so we don't reach the SDK.
    helper.get_client = MagicMock(return_value=(MagicMock(name="client"), "TOK"))
    helper.build_body = MagicMock(side_effect=lambda model, params: {
        "_model": model, **{k: v for k, v in params.items() if v is not None}
    })
    helper.call_api = recorder
    return recorder, factory


def _capture_exit(helper, fn, *args, **kwargs):
    """Run a helper entrypoint that's expected to terminate via
    exit_json or fail_json. Returns (status, kwargs) where status is
    "exit" or "fail" (mapped from the conftest SystemExit code: 0/1)."""
    try:
        fn(*args, **kwargs)
    except SystemExit as e:
        status = "exit" if getattr(e, "code", 0) == 0 else "fail"
        return status, getattr(e, "kwargs", {})
    pytest.fail(f"{fn.__name__} returned without calling exit_json/fail_json")


# ---------------------------------------------------------------------------
# run_info_module
# ---------------------------------------------------------------------------


def test_run_info_module_calls_sdk_and_exits_unchanged(helper, fake_ansible_module):
    recorder, _ = _drive(
        helper,
        params={"name": "rolex"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"get_role": {"name": "rolex", "rules": []}},
    )
    status, kwargs = _capture_exit(
        helper,
        helper.run_info_module,
        argument_spec={"name": {"type": "str"}},
        sdk_call=("GetRole", "get_role"),
    )
    assert status == "exit"
    assert kwargs["changed"] is False
    assert kwargs["result"] == {"name": "rolex", "rules": []}
    assert [inv[0] for inv in recorder.invocations] == ["get_role"]


def test_run_info_module_handles_none_response(helper, fake_ansible_module):
    """Info modules must coerce a None SDK response into an empty dict so
    Ansible doesn't see `result: null` (which fails downstream filters)."""
    recorder, _ = _drive(
        helper, params={}, fake_ansible_module=fake_ansible_module,
        call_responses={"list_items": None},
    )
    status, kwargs = _capture_exit(
        helper,
        helper.run_info_module,
        argument_spec={},
        sdk_call=("ListItems", "list_items"),
    )
    assert status == "exit"
    assert kwargs["result"] == {}


# ---------------------------------------------------------------------------
# run_action_module
# ---------------------------------------------------------------------------


def test_run_action_module_calls_sdk_and_exits_changed(helper, fake_ansible_module):
    recorder, _ = _drive(
        helper,
        params={"plaintext": "hello"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"encrypt": {"ciphertext": "xyz"}},
    )
    status, kwargs = _capture_exit(
        helper,
        helper.run_action_module,
        argument_spec={"plaintext": {"type": "str"}},
        sdk_call=("Encrypt", "encrypt"),
    )
    assert status == "exit"
    assert kwargs["changed"] is True
    assert kwargs["result"] == {"ciphertext": "xyz"}
    assert [inv[0] for inv in recorder.invocations] == ["encrypt"]


# ---------------------------------------------------------------------------
# run_standard_crud
# ---------------------------------------------------------------------------


def _crud_kwargs(immutable=False, idempotent=False, required_if=None,
                 read_key="name"):
    return dict(
        argument_spec={
            "state": {"type": "str", "choices": ["present", "absent"],
                      "default": "present"},
            "name": {"type": "str"},
            "value": {"type": "str"},
        },
        resource_label="thing",
        sdk_create=("ThingCreate", "thing_create"),
        sdk_update=None if (immutable or idempotent) else ("ThingUpdate", "thing_update"),
        sdk_delete=("ThingDelete", "thing_delete"),
        sdk_read=("ThingGet", "thing_get"),
        read_key=read_key,
        required_if=required_if,
        immutable=immutable,
        idempotent=idempotent,
    )


def test_run_standard_crud_absent_when_missing_no_op(helper, fake_ansible_module):
    recorder, _ = _drive(
        helper,
        params={"state": "absent", "name": "x"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": None},  # not found
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is False
    assert "already absent" in kwargs["msg"]
    assert [inv[0] for inv in recorder.invocations] == ["thing_get"]


def test_run_standard_crud_absent_when_present_deletes(helper, fake_ansible_module):
    recorder, _ = _drive(
        helper,
        params={"state": "absent", "name": "x"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x"}, "thing_delete": {"ok": True}},
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is True
    assert [inv[0] for inv in recorder.invocations] == ["thing_get", "thing_delete"]


def test_run_standard_crud_present_when_missing_creates(helper, fake_ansible_module):
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "v"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": None, "thing_create": {"id": 1}},
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is True
    assert [inv[0] for inv in recorder.invocations] == ["thing_get", "thing_create"]


def test_run_standard_crud_present_when_exists_no_drift(helper, fake_ansible_module):
    """compute_diff returns no drift when the resource value matches; helper
    must exit changed=False without touching update."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "v"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x", "value": "v"}},
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is False
    assert [inv[0] for inv in recorder.invocations] == ["thing_get"]


def test_run_standard_crud_present_when_exists_drift_updates(helper, fake_ansible_module):
    """Drift detected -> update is called and diff metadata is emitted."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "new"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x", "value": "old"},
                        "thing_update": {"ok": True}},
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is True
    assert [inv[0] for inv in recorder.invocations] == ["thing_get", "thing_update"]
    assert "diff" in kwargs


def test_run_standard_crud_check_mode_create(helper, fake_ansible_module):
    """In check_mode, a would-be create must NOT call SDK create."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "v"},
        fake_ansible_module=fake_ansible_module,
        check_mode=True,
        call_responses={"thing_get": None},
    )
    status, kwargs = _capture_exit(helper, helper.run_standard_crud, **_crud_kwargs())
    assert status == "exit"
    assert kwargs["changed"] is True
    assert [inv[0] for inv in recorder.invocations] == ["thing_get"]  # no create call


def test_run_standard_crud_immutable_drift_fails(helper, fake_ansible_module):
    """immutable=True + drift -> fail_json with diff explaining recreate."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "new"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x", "value": "old"}},
    )
    status, kwargs = _capture_exit(
        helper, helper.run_standard_crud, **_crud_kwargs(immutable=True)
    )
    assert status == "fail"
    assert "immutable" in kwargs["msg"]
    assert "diff" in kwargs
    # No update was ever called because there's no update endpoint.
    assert all(inv[0] != "thing_update" for inv in recorder.invocations)


def test_run_standard_crud_idempotent_existing_skips_drift(helper, fake_ansible_module):
    """idempotent=True + resource exists -> no-op without drift detection.
    Even when fields differ, we trust the upstream Set endpoint."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x", "value": "different-from-current"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x", "value": "current"}},
    )
    status, kwargs = _capture_exit(
        helper, helper.run_standard_crud, **_crud_kwargs(idempotent=True)
    )
    assert status == "exit"
    assert kwargs["changed"] is False
    # Drift was not even computed -> only the read was called.
    assert [inv[0] for inv in recorder.invocations] == ["thing_get"]


def test_run_standard_crud_idempotent_creates_when_missing(helper, fake_ansible_module):
    """idempotent=True + resource missing -> still creates."""
    recorder, _ = _drive(
        helper,
        params={"state": "present", "name": "x"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": None, "thing_create": {"ok": True}},
    )
    status, kwargs = _capture_exit(
        helper, helper.run_standard_crud, **_crud_kwargs(idempotent=True)
    )
    assert status == "exit"
    assert kwargs["changed"] is True
    assert [inv[0] for inv in recorder.invocations] == ["thing_get", "thing_create"]


def test_run_standard_crud_immutable_and_idempotent_is_an_error(helper, fake_ansible_module):
    """The two flags express incompatible semantics: immutable rejects
    drift, idempotent treats all existing as no-change. Catch the
    contradiction at the call site instead of letting a wrong-flag
    combination silently default to 'no-op forever'."""
    _drive(
        helper, params={"state": "present", "name": "x"},
        fake_ansible_module=fake_ansible_module,
        call_responses={"thing_get": {"name": "x"}},
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        helper.run_standard_crud(**_crud_kwargs(immutable=True, idempotent=True))
