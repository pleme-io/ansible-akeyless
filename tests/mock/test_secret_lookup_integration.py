# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `secret` lookup plugin.
# Uses the shared mock-server infrastructure in
# tests/mock/_lookup_helpers.py.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import MagicMock

from .conftest import FakeApiException
from ._lookup_helpers import (
    LookupMockServer, install_lookup_stubs, load_lookup_module,
    snapshot_modules, restore_modules,
)


@pytest.fixture
def lookup_server():
    """Returns (server, lookup_instance). Stubs are reset on teardown."""
    saved = snapshot_modules()
    server = LookupMockServer()
    install_lookup_stubs(
        server,
        sdk_method_name="get_secret_value",
        extra_akeyless_attrs={
            "GetSecretValue": MagicMock(name="akeyless.GetSecretValue"),
        },
    )
    mod = load_lookup_module(
        "secret.py", "akeyless_secret_lookup_mock_integration"
    )
    instance = mod.LookupModule()
    try:
        yield server, instance
    finally:
        restore_modules(saved)


# ---------------------------------------------------------------------------
# Wire-level fetch tests
# ---------------------------------------------------------------------------


def test_single_secret_fetch(lookup_server):
    """Single-term lookup: dispatches one get_secret_value call,
    returns a one-element list aligned to the input term."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/app/db/password": "rotated-value"},
    )
    out = lookup.run(
        ["/app/db/password"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert out == ["rotated-value"]
    assert [c[0] for c in server.calls] == ["get_secret_value"]


def test_multi_secret_fetch_returns_input_order(lookup_server):
    """N-term lookup: get_secret_value is called ONCE (batch), result
    is re-shaped into a list aligned to input order regardless of
    response key order."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={
            "/c": "value-c",
            "/a": "value-a",
            "/b": "value-b",
        },
    )
    out = lookup.run(
        ["/a", "/b", "/c"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert out == ["value-a", "value-b", "value-c"]
    # ONE call -- the lookup batches via GetSecretValue(names=[...]).
    assert len([c for c in server.calls if c[0] == "get_secret_value"]) == 1


def test_missing_secret_raises_lookup_error(lookup_server):
    """If a requested term is not in the response dict, the lookup
    must raise AnsibleLookupError so the playbook fails noisily
    rather than silently inserting None into the rendered template."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/found": "value"},
    )
    with pytest.raises(AnsibleLookupError, match=r"/missing.*not found"):
        lookup.run(
            ["/missing"],
            variables={},
            access_id="p-test", access_key="k-test",
        )


def test_api_exception_translated_to_lookup_error(lookup_server):
    """ApiException from get_secret_value -> AnsibleLookupError with
    status + body in the message (the @akeyless_lookup decorator's
    contract)."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        raises=FakeApiException(status=403, body="forbidden"),
    )
    with pytest.raises(AnsibleLookupError, match=r"403.*forbidden"):
        lookup.run(
            ["/x"],
            variables={},
            access_id="p-test", access_key="k-test",
        )


def test_pre_issued_token_skips_auth_call(lookup_server):
    """When the caller supplies `token=...`, the lookup MUST NOT
    make an auth() call -- it uses the token directly."""
    server, lookup = lookup_server
    server.on(
        "get_secret_value",
        response={"/x": "value-x"},
    )
    out = lookup.run(
        ["/x"],
        variables={},
        token="pre-issued-token",  # no access_id needed
    )
    assert out == ["value-x"]


def test_invalid_response_type_raises_lookup_error(lookup_server):
    """If the SDK response normalises to something other than a dict
    (e.g. a list of secrets), the lookup must fail explicitly rather
    than blindly indexing."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    # Raw non-dict response (no to_dict method).
    server.on("get_secret_value", response=["not", "a", "dict"])
    with pytest.raises(AnsibleLookupError, match=r"Unexpected.*response type"):
        lookup.run(
            ["/x"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
