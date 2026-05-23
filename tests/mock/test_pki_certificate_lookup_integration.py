# Copyright: (c) 2026, pleme-io
# MIT License
#
# Wire-level integration tests for the `pki_certificate` lookup
# plugin. Uses the shared mock-server infrastructure in
# tests/mock/_lookup_helpers.py. Additionally exercises the
# extra_opts path of @akeyless_lookup (common_name / alt_names /
# ttl / key_data_base64 flowing through compact_kwargs).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from .conftest import FakeApiException
from ._lookup_helpers import (
    LookupMockServer, install_lookup_stubs, load_lookup_module,
    snapshot_modules, restore_modules,
)


# A mutable dict the body-recorder writes into so tests can assert
# on what kwargs the lookup passed to GetPKICertificate.
_captured_body: dict = {}


@pytest.fixture
def lookup_server():
    saved = snapshot_modules()
    server = LookupMockServer()
    _captured_body.clear()
    install_lookup_stubs(
        server,
        sdk_method_name="get_pki_certificate",
        sdk_body_class_name="GetPKICertificate",
        body_capture=_captured_body,
    )
    mod = load_lookup_module(
        "pki_certificate.py",
        "akeyless_pki_certificate_lookup_mock_integration",
    )
    instance = mod.LookupModule()
    try:
        yield server, instance, _captured_body
    finally:
        restore_modules(saved)


# ---------------------------------------------------------------------------
# Cert issuance + extra_opts propagation
# ---------------------------------------------------------------------------


def test_issue_with_minimum_args(lookup_server):
    """Single issuer name, no CN/SAN/TTL -- the body must carry only
    the cert_issuer_name + token (not None/empty extras)."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={
            "cert": "-----BEGIN CERTIFICATE-----\nA\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nK\n-----END RSA PRIVATE KEY-----",
        },
    )
    out = lookup.run(
        ["/pki/server-issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 1
    assert "cert" in out[0]
    assert "private_key" in out[0]
    assert captured["cert_issuer_name"] == "/pki/server-issuer"
    assert captured["token"] == "mock-token"
    assert "common_name" not in captured
    assert "alt_names" not in captured


def test_extra_opts_propagated_to_body(lookup_server):
    """When common_name + alt_names + ttl are supplied, they must
    flow through compact_kwargs into the GetPKICertificate body."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM", "private_key": "KEY"},
    )
    lookup.run(
        ["/pki/server-issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
        common_name="web.example.com",
        alt_names="web,svc",
        ttl=3600,
    )
    assert captured["common_name"] == "web.example.com"
    assert captured["alt_names"] == "web,svc"
    assert captured["ttl"] == 3600


def test_empty_string_extras_dropped(lookup_server):
    """compact_kwargs drops empty strings -- a caller passing
    common_name='' should NOT cause the body to ship an empty
    CN field (Akeyless might reject)."""
    server, lookup, captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM"},
    )
    lookup.run(
        ["/pki/issuer"],
        variables={},
        access_id="p-test", access_key="k-test",
        common_name="",       # should be dropped
        alt_names="real-san",  # should pass through
        ttl=None,             # should be dropped
    )
    assert "common_name" not in captured
    assert captured["alt_names"] == "real-san"
    assert "ttl" not in captured


def test_per_term_loop_for_multiple_issuers(lookup_server):
    """Each issuer term triggers one get_pki_certificate call."""
    server, lookup, _captured = lookup_server
    server.on(
        "get_pki_certificate",
        response={"cert": "PEM"},
    )
    out = lookup.run(
        ["/pki/a", "/pki/b"],
        variables={},
        access_id="p-test", access_key="k-test",
    )
    assert len(out) == 2
    assert len([c for c in server.calls if c[0] == "get_pki_certificate"]) == 2


def test_api_exception_includes_issuer_name(lookup_server):
    """ApiException must surface the failing issuer name."""
    from ansible.errors import AnsibleLookupError
    server, lookup, _captured = lookup_server
    server.on(
        "get_pki_certificate",
        raises=FakeApiException(status=403, body="forbidden"),
    )
    with pytest.raises(AnsibleLookupError, match=r"unauthorized-issuer.*403"):
        lookup.run(
            ["/pki/unauthorized-issuer"],
            variables={},
            access_id="p-test", access_key="k-test",
        )
