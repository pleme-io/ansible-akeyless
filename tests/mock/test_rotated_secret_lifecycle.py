# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: full CRUD lifecycle on
# `rotated_secret_postgresql`. Representative of the rotated_secret_*
# family (~10 modules; Cassandra, MSSQL, MongoDB, MySQL, PostgreSQL,
# LDAP, custom, ...).
#
# Distinct shape from dynamic_secret_*: rotated secrets reuse the
# describe_item / delete_item SDK methods that static_secret uses,
# but with per-DB-type create/update endpoints. Wire coverage here
# pins both the read/delete path (shared with static_secret) AND
# the create/update path (distinct per producer).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def _base_params(**overrides):
    base = {
        "name": "/rotated/db/app-rw",
        "target_name": "/targets/prod-db",
        "rotation_hour": 2,
        "rotation_interval": "30",
        "authentication_credentials": "use-user-creds",
        "rotated_username": "app_rw",
        "rotated_password": "current-password",
        "access_id": "p-test",
        "access_key": "k-test",
        "state": "present",
    }
    base.update(overrides)
    return base


def test_create_when_absent(mock_server):
    """describe_item 404 -> rotated_secret_create_postgresql fires
    + changed=True."""
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=404, body="rotated secret not found"),
    )
    mock_server.on(
        "rotated_secret_create_postgresql",
        response={"item_name": "/rotated/db/app-rw", "created": True},
    )
    payload, code = mock_server.run_module(
        "rotated_secret_postgresql.py", params=_base_params(),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [n for n, _b in mock_server.calls]
    assert methods == ["describe_item", "rotated_secret_create_postgresql"]


def test_update_when_rotation_interval_changes(mock_server):
    """Existing rotated secret with different rotation_interval ->
    rotated_secret_update_postgresql fires."""
    mock_server.on(
        "describe_item",
        response={
            "item_name": "/rotated/db/app-rw",
            "item_type": "ROTATED_SECRET",
            "rotation_interval": "60",  # different from _base_params 30
            "target_name": "/targets/prod-db",
        },
    )
    mock_server.on(
        "rotated_secret_update_postgresql",
        response={"item_name": "/rotated/db/app-rw", "updated": True},
    )
    payload, code = mock_server.run_module(
        "rotated_secret_postgresql.py",
        params=_base_params(rotation_interval="30"),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    assert "rotated_secret_update_postgresql" in [n for n, _ in mock_server.calls]


def test_delete_when_present(mock_server):
    """state: absent + rotated secret exists -> delete_item fires.
    Uses the SHARED delete_item SDK method (same as static_secret)."""
    mock_server.on(
        "describe_item",
        response={"item_name": "/rotated/db/app-rw"},
    )
    mock_server.on(
        "delete_item",
        response={"item_name": "/rotated/db/app-rw", "deleted": True},
    )
    payload, code = mock_server.run_module(
        "rotated_secret_postgresql.py",
        params=_base_params(
            state="absent",
            target_name=None, rotation_hour=None,
            rotation_interval=None, authentication_credentials=None,
            rotated_username=None, rotated_password=None,
        ),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [n for n, _b in mock_server.calls]
    assert methods == ["describe_item", "delete_item"]


def test_delete_idempotent_when_absent(mock_server):
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=404, body="not found"),
    )
    payload, code = mock_server.run_module(
        "rotated_secret_postgresql.py",
        params=_base_params(
            state="absent",
            target_name=None, rotation_hour=None,
            rotation_interval=None, authentication_credentials=None,
            rotated_username=None, rotated_password=None,
        ),
    )
    assert code == 0, payload
    assert payload.get("changed") is False
