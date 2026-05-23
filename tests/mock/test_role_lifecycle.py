# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration test: full CRUD lifecycle on the `role` module.
#
# Pattern: register stub responses on the MockServer, run main() against
# it, assert on the exit_json payload and the recorded SDK call sequence.
# This is the closest we can get to "what would the real playbook do"
# without a live Akeyless tenant -- the SDK is exercised end-to-end with
# only the wire layer mocked.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def test_create_when_absent(mock_server):
    """GET 404 -> create_role is called once -> exit changed=True."""
    mock_server.on("get_role", raises=FakeApiException(status=404, body="not found"))
    mock_server.on("create_role", response={"role_name": "demo", "created": True})

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "present",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["get_role", "create_role"], methods


def test_update_when_present_and_drift(mock_server):
    """GET returns a current state whose `description` differs from
    the desired param -> compute_diff sees drift -> update_role is
    called once -> changed=True with diff metadata.

    Post-idempotency contract; pre-idempotency the test just checked
    that update fires whenever the resource exists, regardless of
    whether anything actually differed."""
    mock_server.on(
        "get_role",
        response={"role_name": "demo", "description": "old"})
    mock_server.on(
        "update_role",
        response={"role_name": "demo", "updated": True})

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "present",
            "description": "new",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert "update_role" in methods
    assert "create_role" not in methods
    diff = payload.get("diff") or {}
    assert diff.get("before", {}).get("description") == "old"
    assert diff.get("after", {}).get("description") == "new"


def test_no_update_when_in_desired_state(mock_server):
    """When GET returns state matching desired params, the module
    skips update entirely and returns changed=False with the
    'already in desired state' msg. This is the whole point of the
    compute_diff layer -- honest convergence vs always-changed."""
    mock_server.on(
        "get_role",
        response={"role_name": "demo", "description": "stable"})
    mock_server.on("update_role", response={"updated": True})

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "present",
            "description": "stable",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    assert "already in desired state" in (payload.get("msg") or "")
    methods = [name for name, _body in mock_server.calls]
    assert "update_role" not in methods
    assert "create_role" not in methods


def test_delete_when_present(mock_server):
    """GET 200 + state=absent -> delete_role called -> changed=True."""
    mock_server.on("get_role", response={"role_name": "demo"})
    mock_server.on("delete_role", response={"deleted": True})

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "absent",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods[-1] == "delete_role"


def test_delete_noop_when_already_absent(mock_server):
    """GET 404 + state=absent -> no mutation -> changed=False."""
    mock_server.on("get_role", raises=FakeApiException(status=404, body="not found"))

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "absent",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    methods = [name for name, _body in mock_server.calls]
    assert "delete_role" not in methods


def test_check_mode_skips_mutations(mock_server):
    """check_mode=True with state=present, current exists -> no mutation."""
    mock_server.on("get_role", response={"role_name": "demo"})

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "present",
        },
        check_mode=True,
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["get_role"]


def test_read_resource_propagates_api_error(mock_server):
    """Non-404 ApiException from get_role -> module.fail_json with status."""
    mock_server.on(
        "get_role",
        raises=FakeApiException(status=500, body="upstream blew up"),
    )

    payload, code = mock_server.run_module(
        "role.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
            "state": "present",
        },
    )

    assert code == 1, payload
    assert payload.get("status") == 500
