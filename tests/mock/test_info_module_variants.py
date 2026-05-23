# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration for info-module variants beyond role_info.
# Covers the LIST-shape SDK calls (PoliciesList, TargetsList, etc.)
# which differ from the single-resource GET shape role_info exercises.
# Both go through run_info_module but the list shape returns an
# array under .result while the get shape returns a dict.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


def test_policies_info_returns_list(mock_server):
    """policies_info wraps PoliciesList -- the response is an array
    of policy dicts, not a single resource. The module must surface
    it under .result and emit changed=False."""
    mock_server.on(
        "policies_list",
        response={
            "policies": [
                {"path": "/secrets/*", "rule_type": "item-rule"},
                {"path": "/auth/*", "rule_type": "auth-method-rule"},
            ],
        },
    )
    payload, code = mock_server.run_module(
        "policies_info.py",
        params={"access_id": "p-test", "access_key": "k-test"},
    )
    assert code == 0, payload
    assert payload.get("changed") is False, (
        "info modules must always emit changed=False"
    )
    result = payload.get("result") or {}
    assert "policies" in result, result
    assert len(result["policies"]) == 2


def test_targets_info_returns_target_array(mock_server):
    """targets_info wraps ListTargets -- same list shape as
    policies_list. (The SDK method name doesn't always mirror the
    module name; targets_info -> list_targets.)"""
    mock_server.on(
        "list_targets",
        response={
            "targets": [
                {"target_name": "/targets/prod-db", "target_type": "DB"},
                {"target_name": "/targets/staging-db", "target_type": "DB"},
            ],
        },
    )
    payload, code = mock_server.run_module(
        "targets_info.py",
        params={"access_id": "p-test", "access_key": "k-test"},
    )
    assert code == 0, payload
    assert payload.get("changed") is False
    result = payload.get("result") or {}
    assert len(result.get("targets") or []) == 2


def test_info_module_propagates_api_error(mock_server):
    """A 403 from the list endpoint must surface as fail_json -- the
    operator can then debug their access policy. Silently returning
    empty would hide misconfiguration."""
    mock_server.on(
        "policies_list",
        raises=FakeApiException(status=403, body="permission denied"),
    )
    payload, code = mock_server.run_module(
        "policies_info.py",
        params={"access_id": "p-test", "access_key": "k-test"},
    )
    assert code == 1, payload
    msg = payload.get("msg", "")
    assert "403" in msg or "permission" in msg.lower()


def test_validate_certificate_challenge_action(mock_server):
    """Validate-* action module: ValidateCertificateChallenge
    response surfaces under .result + changed=True (action module
    contract). Distinct from the encrypt/decrypt path -- this is a
    cert-lifecycle action."""
    mock_server.on(
        "validate_certificate_challenge",
        response={"status": "validated", "domain": "example.com"},
    )
    payload, code = mock_server.run_module(
        "validate_certificate_challenge.py",
        params={
            "domain": "example.com",
            "cert_issuer_name": "/pki/letsencrypt",
            "token": "challenge-token",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    assert result.get("status") == "validated"


def test_uid_list_children_returns_children(mock_server):
    """uid_list_children action returns the tree of UID child tokens.
    Important for the PRM-1790 customer flow -- token rotation +
    inspection is the core use case."""
    mock_server.on(
        "uid_list_children",
        response={
            "children": [
                {"id": "child-1", "ttl": 3600},
                {"id": "child-2", "ttl": 1800},
            ],
        },
    )
    payload, code = mock_server.run_module(
        "uid_list_children.py",
        params={
            "auth_method_name": "/auth/uid",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    assert len(result.get("children") or []) == 2
