# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `dynamic_secret` lookup plugin.
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
    saved = snapshot_modules()
    server = LookupMockServer()
    install_lookup_stubs(
        server,
        sdk_method_name="get_dynamic_secret_value",
        extra_akeyless_attrs={
            "GetDynamicSecretValue": MagicMock(name="akeyless.GetDynamicSecretValue"),
        },
    )
    mod = load_lookup_module(
        "dynamic_secret.py",
        "akeyless_dynamic_secret_lookup_mock_integration",
    )
    instance = mod.LookupModule()
    try:
        yield server, instance
    finally:
        restore_modules(saved)


# ---------------------------------------------------------------------------
# Per-term dispatch semantics
# ---------------------------------------------------------------------------


def test_single_term_one_call(lookup_server):
    """Single term -> single get_dynamic_secret_value call,
    response unwrapped to dict via to_dict()."""
    server, lookup = lookup_server
    server.on(
        "get_dynamic_secret_value",
        response={"user": "tmp_user", "password": "tmp_pass", "ttl": 1800},
    )
    out = lookup.run(
        ["/dynamic/db/readonly"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 1
    assert out[0]["user"] == "tmp_user"
    assert out[0]["password"] == "tmp_pass"
    assert len([c for c in server.calls if c[0] == "get_dynamic_secret_value"]) == 1


def test_multi_term_calls_per_term(lookup_server):
    """N terms -> N get_dynamic_secret_value calls (per-term mode,
    not batched). Result list aligned to input order."""
    server, lookup = lookup_server
    call_count = {"n": 0}
    responses = [
        {"user": "u_a", "password": "p_a"},
        {"user": "u_b", "password": "p_b"},
        {"user": "u_c", "password": "p_c"},
    ]
    def _per_call(_body):
        idx = call_count["n"]
        call_count["n"] += 1
        return responses[idx]
    server.on(
        "get_dynamic_secret_value",
        callable_factory=_per_call,
    )
    out = lookup.run(
        ["/a", "/b", "/c"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 3
    assert out[0]["user"] == "u_a"
    assert out[1]["user"] == "u_b"
    assert out[2]["user"] == "u_c"
    assert len([c for c in server.calls if c[0] == "get_dynamic_secret_value"]) == 3


def test_api_exception_per_term_translates_with_term_context(lookup_server):
    """ApiException on a specific term must surface the term name in
    the AnsibleLookupError -- otherwise the operator can't tell
    which dynamic secret broke when one of N requested fails."""
    from ansible.errors import AnsibleLookupError
    server, lookup = lookup_server
    server.on(
        "get_dynamic_secret_value",
        raises=FakeApiException(status=404, body="dynamic secret not found"),
    )
    with pytest.raises(AnsibleLookupError, match=r"missing.*404"):
        lookup.run(
            ["/dynamic/missing"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
