# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: full CRUD lifecycle on the `static_secret`
# module. Static secrets are the most-used resource in the collection
# (the lookup, the action plugin, the inventory plugin all read them),
# so wire-level coverage matters here even more than the role.
#
# Same pattern as test_role_lifecycle.py -- register endpoint
# responses, run main() through the helper, assert on payload + call
# sequence.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def _base_params(**overrides):
    base = {
        "name": "/app/db/password",
        "value": "rotated-password",
        "access_id": "p-test",
        "access_key": "k-test",
        "state": "present",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Create-when-absent (present + 404 -> create_secret)
# ---------------------------------------------------------------------------


def test_create_when_absent(mock_server):
    """describe_item returns 404 -> create_secret fires once ->
    changed=True. Most common first-run shape."""
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=404, body="item not found"),
    )
    mock_server.on(
        "create_secret",
        response={"item_name": "/app/db/password", "created": True},
    )

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["describe_item", "create_secret"], methods


# ---------------------------------------------------------------------------
# Update-on-drift (existing item, different value -> update_secret_val)
# ---------------------------------------------------------------------------


def test_update_when_value_changes(mock_server):
    """describe_item returns existing item; the requested value
    differs from current -> update_secret_val fires + changed=True."""
    mock_server.on(
        "describe_item",
        response={
            "item_name": "/app/db/password",
            "item_type": "STATIC_SECRET",
            "value": "old-password",
        },
    )
    mock_server.on(
        "update_secret_val",
        response={"item_name": "/app/db/password", "updated": True},
    )

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(value="new-password"),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert "update_secret_val" in methods


# ---------------------------------------------------------------------------
# Idempotency: existing item, matching value -> no update call
# ---------------------------------------------------------------------------


def test_no_update_when_value_matches(mock_server):
    """When describe_item's returned value matches the requested
    value, update_secret_val must NOT be called -- compute_diff
    surfaces no drift."""
    mock_server.on(
        "describe_item",
        response={
            "item_name": "/app/db/password",
            "item_type": "STATIC_SECRET",
            "value": "rotated-password",  # matches _base_params()
        },
    )
    # Intentionally NOT registering update_secret_val so a call
    # would fail with "no handler".

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(),
    )

    assert code == 0, payload
    methods = [name for name, _body in mock_server.calls]
    assert "update_secret_val" not in methods, (
        f"update fired despite no drift: {methods}"
    )


# ---------------------------------------------------------------------------
# Delete-when-present
# ---------------------------------------------------------------------------


def test_delete_when_present(mock_server):
    """state: absent + item exists -> delete_item fires + changed=True."""
    mock_server.on(
        "describe_item",
        response={"item_name": "/app/db/password"},
    )
    mock_server.on(
        "delete_item",
        response={"item_name": "/app/db/password", "deleted": True},
    )

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(state="absent", value=None),
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["describe_item", "delete_item"], methods


# ---------------------------------------------------------------------------
# Delete is idempotent: absent + 404 -> no delete call, changed=False
# ---------------------------------------------------------------------------


def test_delete_noop_when_already_absent(mock_server):
    """state: absent + describe returns 404 -> no delete call,
    changed=False. Important for re-runs of a removal playbook."""
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=404, body="not found"),
    )

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(state="absent", value=None),
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["describe_item"], methods


# ---------------------------------------------------------------------------
# Check mode: no mutations called regardless of state
# ---------------------------------------------------------------------------


def test_check_mode_skips_mutations(mock_server):
    """In check mode, neither create_secret nor update_secret_val are
    called -- the module reports what would change without doing it."""
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=404, body="not found"),
    )
    # No mutation handlers registered; any call would 500.

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(), check_mode=True,
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    methods = [name for name, _body in mock_server.calls]
    assert "create_secret" not in methods, (
        f"create_secret called in check mode: {methods}"
    )


# ---------------------------------------------------------------------------
# Wire-level error propagation: any non-404 from describe propagates
# ---------------------------------------------------------------------------


def test_describe_500_propagates_as_fail(mock_server):
    """A 500 (or any non-404) from describe_item must surface as
    fail_json, not silently treated as 'absent'. 404-tolerance is
    specifically about 'resource not present'; other errors are
    real failures."""
    mock_server.on(
        "describe_item",
        raises=FakeApiException(status=500, body="gateway internal error"),
    )

    payload, code = mock_server.run_module(
        "static_secret.py", params=_base_params(),
    )

    assert code == 1, payload
    msg = payload.get("msg", "")
    assert "500" in msg or "internal" in msg.lower(), (
        f"500 propagation lost context: {msg!r}"
    )
