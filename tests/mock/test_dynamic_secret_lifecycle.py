# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: full CRUD lifecycle on
# `dynamic_secret_postgresql`. Representative of the dynamic_secret_*
# family -- they all wrap the same DynamicSecretGet / DynamicSecretDelete
# shape with a per-producer create/update pair.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def _base_params(**overrides):
    base = {
        "name": "/dynamic/db/postgres-readonly",
        "target_name": "/targets/prod-db",
        "user_ttl": "30m",
        "postgresql_db_name": "appdb",
        "postgresql_statements": "CREATE USER ...",
        "access_id": "p-test",
        "access_key": "k-test",
        "state": "present",
    }
    base.update(overrides)
    return base


def test_create_when_absent(mock_server):
    """dynamic_secret_get 404 -> dynamic_secret_create_postgre_sql
    fires + changed=True."""
    mock_server.on(
        "dynamic_secret_get",
        raises=FakeApiException(status=404, body="dynamic secret not found"),
    )
    mock_server.on(
        "dynamic_secret_create_postgre_sql",
        response={"name": "/dynamic/db/postgres-readonly", "created": True},
    )
    payload, code = mock_server.run_module(
        "dynamic_secret_postgresql.py", params=_base_params(),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [n for n, _b in mock_server.calls]
    assert methods == ["dynamic_secret_get", "dynamic_secret_create_postgre_sql"]


def test_update_when_ttl_changes(mock_server):
    """Existing dynamic secret with different user_ttl ->
    dynamic_secret_update_postgre_sql fires."""
    mock_server.on(
        "dynamic_secret_get",
        response={
            "name": "/dynamic/db/postgres-readonly",
            "user_ttl": "1h",
            "target_name": "/targets/prod-db",
        },
    )
    mock_server.on(
        "dynamic_secret_update_postgre_sql",
        response={"name": "/dynamic/db/postgres-readonly", "updated": True},
    )
    payload, code = mock_server.run_module(
        "dynamic_secret_postgresql.py",
        params=_base_params(user_ttl="30m"),  # differs from "1h"
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    assert "dynamic_secret_update_postgre_sql" in [n for n, _ in mock_server.calls]


def test_delete_when_present(mock_server):
    """state: absent + dynamic secret exists -> dynamic_secret_delete."""
    mock_server.on(
        "dynamic_secret_get",
        response={"name": "/dynamic/db/postgres-readonly"},
    )
    mock_server.on(
        "dynamic_secret_delete",
        response={"name": "/dynamic/db/postgres-readonly", "deleted": True},
    )
    payload, code = mock_server.run_module(
        "dynamic_secret_postgresql.py",
        params=_base_params(state="absent",
                             target_name=None, user_ttl=None,
                             postgresql_db_name=None, postgresql_statements=None),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [n for n, _b in mock_server.calls]
    assert methods == ["dynamic_secret_get", "dynamic_secret_delete"]


def test_delete_idempotent_when_already_absent(mock_server):
    mock_server.on(
        "dynamic_secret_get",
        raises=FakeApiException(status=404, body="not found"),
    )
    payload, code = mock_server.run_module(
        "dynamic_secret_postgresql.py",
        params=_base_params(state="absent",
                             target_name=None, user_ttl=None,
                             postgresql_db_name=None, postgresql_statements=None),
    )
    assert code == 0, payload
    assert payload.get("changed") is False
