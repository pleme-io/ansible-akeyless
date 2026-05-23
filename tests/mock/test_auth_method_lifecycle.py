# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: full CRUD lifecycle on `auth_method_oidc`.
# Representative of the 16 auth_method_* modules -- they all wrap
# the same get_auth_method / delete_auth_method shape with a
# per-type create/update pair. Wire coverage here exercises the path
# every auth method module shares.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def _base_params(**overrides):
    base = {
        "name": "/auth/oidc/prod",
        "issuer": "https://issuer.example.com",
        "client_id": "client-xxx",
        "client_secret": "secret-yyy",
        "access_id": "p-test",
        "access_key": "k-test",
        "state": "present",
    }
    base.update(overrides)
    return base


def test_create_when_absent(mock_server):
    """get_auth_method 404 -> auth_method_create_oidc fires once."""
    mock_server.on(
        "get_auth_method",
        raises=FakeApiException(status=404, body="auth method not found"),
    )
    mock_server.on(
        "auth_method_create_oidc",
        response={"auth_method_name": "/auth/oidc/prod", "created": True},
    )
    payload, code = mock_server.run_module(
        "auth_method_oidc.py", params=_base_params(),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _b in mock_server.calls]
    assert methods == ["get_auth_method", "auth_method_create_oidc"], methods


def test_update_when_issuer_changes(mock_server):
    """get_auth_method returns existing method with different
    issuer -> auth_method_update_oidc fires + changed=True."""
    mock_server.on(
        "get_auth_method",
        response={
            "auth_method_name": "/auth/oidc/prod",
            "issuer": "https://old-issuer.example.com",
            "client_id": "client-xxx",
        },
    )
    mock_server.on(
        "auth_method_update_oidc",
        response={"auth_method_name": "/auth/oidc/prod", "updated": True},
    )
    payload, code = mock_server.run_module(
        "auth_method_oidc.py",
        params=_base_params(issuer="https://new-issuer.example.com"),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    assert "auth_method_update_oidc" in [n for n, _ in mock_server.calls]


def test_delete_when_present(mock_server):
    """state: absent + auth method exists -> delete_auth_method fires."""
    mock_server.on(
        "get_auth_method",
        response={"auth_method_name": "/auth/oidc/prod"},
    )
    mock_server.on(
        "delete_auth_method",
        response={"auth_method_name": "/auth/oidc/prod", "deleted": True},
    )
    payload, code = mock_server.run_module(
        "auth_method_oidc.py",
        params=_base_params(state="absent",
                             issuer=None, client_id=None, client_secret=None),
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [n for n, _b in mock_server.calls]
    assert methods == ["get_auth_method", "delete_auth_method"], methods


def test_delete_idempotent_when_absent(mock_server):
    """state: absent + auth method 404 -> no delete call."""
    mock_server.on(
        "get_auth_method",
        raises=FakeApiException(status=404, body="not found"),
    )
    payload, code = mock_server.run_module(
        "auth_method_oidc.py",
        params=_base_params(state="absent",
                             issuer=None, client_id=None, client_secret=None),
    )
    assert code == 0, payload
    assert payload.get("changed") is False
