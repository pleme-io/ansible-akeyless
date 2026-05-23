# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: full CRUD lifecycle on the `target_db`
# module. Targets are the second-most-common resource shape after
# secrets -- they back the dynamic-secret producers, so wire coverage
# here exercises the same code paths the gateway_producer_* modules
# rely on (different sdk_call names but identical run_standard_crud
# helper path).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def _base_params(**overrides):
    base = {
        "name": "/targets/prod-db",
        "db_type": "postgres",
        "host": "db.internal",
        "port": "5432",
        "user_name": "app",
        "pwd": "secret-from-vault",
        "access_id": "p-test",
        "access_key": "k-test",
        "state": "present",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Create-when-absent
# ---------------------------------------------------------------------------


def test_create_when_absent(mock_server):
    """target_get 404 -> target_create_db fires once -> changed=True.
    Mirrors the static-secret create-when-absent path through the
    target_* SDK methods."""
    mock_server.on(
        "target_get",
        raises=FakeApiException(status=404, body="target not found"),
    )
    mock_server.on(
        "target_create_db",
        response={"target_name": "/targets/prod-db", "created": True},
    )

    payload, code = mock_server.run_module(
        "target_db.py", params=_base_params(),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["target_get", "target_create_db"], methods


# ---------------------------------------------------------------------------
# Update-when-drift (existing target whose host/port changed)
# ---------------------------------------------------------------------------


def test_update_when_host_changes(mock_server):
    """target_get returns existing target with different host ->
    target_update_db fires + changed=True."""
    mock_server.on(
        "target_get",
        response={
            "target_name": "/targets/prod-db",
            "target_type": "DB",
            "host": "old-db.internal",
            "port": "5432",
        },
    )
    mock_server.on(
        "target_update_db",
        response={"target_name": "/targets/prod-db", "updated": True},
    )

    payload, code = mock_server.run_module(
        "target_db.py", params=_base_params(host="new-db.internal"),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert "target_update_db" in methods


# ---------------------------------------------------------------------------
# Delete-when-present
# ---------------------------------------------------------------------------


def test_delete_when_present(mock_server):
    """state: absent + target exists -> target_delete + changed=True."""
    mock_server.on(
        "target_get",
        response={"target_name": "/targets/prod-db"},
    )
    mock_server.on(
        "target_delete",
        response={"target_name": "/targets/prod-db", "deleted": True},
    )

    payload, code = mock_server.run_module(
        "target_db.py",
        params=_base_params(state="absent",
                             db_type=None, host=None, port=None,
                             user_name=None, pwd=None),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["target_get", "target_delete"], methods


# ---------------------------------------------------------------------------
# Delete is idempotent
# ---------------------------------------------------------------------------


def test_delete_noop_when_already_absent(mock_server):
    """state: absent + target_get 404 -> no delete call, changed=False."""
    mock_server.on(
        "target_get",
        raises=FakeApiException(status=404, body="not found"),
    )

    payload, code = mock_server.run_module(
        "target_db.py",
        params=_base_params(state="absent",
                             db_type=None, host=None, port=None,
                             user_name=None, pwd=None),
    )

    assert code == 0, payload
    assert payload.get("changed") is False


# ---------------------------------------------------------------------------
# Wire-level error from non-404 propagates
# ---------------------------------------------------------------------------


def test_target_get_503_propagates_as_fail(mock_server):
    """503 from target_get must surface as fail_json -- never silently
    treated as 'absent'. 503 = gateway unhealthy, retry instead of
    spuriously creating a fresh resource."""
    mock_server.on(
        "target_get",
        raises=FakeApiException(status=503, body="service unavailable"),
    )

    payload, code = mock_server.run_module(
        "target_db.py", params=_base_params(),
    )

    assert code == 1, payload
    msg = payload.get("msg", "")
    assert "503" in msg or "unavailable" in msg.lower()
