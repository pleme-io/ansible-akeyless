# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration: crypto action modules (encrypt / decrypt).
# Covers the run_action_module path -- distinct from run_standard_crud
# (no get/create/update; just a single SDK call + return).
#
# Important contract this pins: action modules MUST always return
# changed=True (they're side-effecting operations, the caller's
# intent is to perform the action) AND the response value is
# surfaced under .result on the exit_json payload.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .conftest import FakeApiException


# ---------------------------------------------------------------------------
# encrypt
# ---------------------------------------------------------------------------


def test_encrypt_returns_ciphertext(mock_server):
    """encrypt action calls the Encrypt SDK method once + surfaces
    the ciphertext under .result."""
    mock_server.on(
        "encrypt",
        response={"result": "ENCRYPTED_BLOB_BASE64"},
    )
    payload, code = mock_server.run_module(
        "encrypt.py",
        params={
            "key_name": "/keys/app-encrypt",
            "plaintext": "secret-data",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True, (
        "action modules must always report changed=True"
    )
    # The wrapped SDK response surfaces under .result.
    result = payload.get("result") or {}
    assert result.get("result") == "ENCRYPTED_BLOB_BASE64"
    assert [c[0] for c in mock_server.calls] == ["encrypt"]


def test_encrypt_propagates_api_failure(mock_server):
    """A 400 from Encrypt (e.g. invalid key) surfaces as fail_json."""
    mock_server.on(
        "encrypt",
        raises=FakeApiException(status=400, body="invalid key version"),
    )
    payload, code = mock_server.run_module(
        "encrypt.py",
        params={
            "key_name": "/keys/missing",
            "plaintext": "data",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 1, payload
    assert "400" in payload.get("msg", "") or "invalid" in payload.get("msg", "").lower()


# ---------------------------------------------------------------------------
# decrypt
# ---------------------------------------------------------------------------


def test_decrypt_returns_plaintext(mock_server):
    mock_server.on(
        "decrypt",
        response={"result": "decrypted-plaintext"},
    )
    payload, code = mock_server.run_module(
        "decrypt.py",
        params={
            "key_name": "/keys/app-encrypt",
            "ciphertext": "ENCRYPTED_BLOB_BASE64",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    assert result.get("result") == "decrypted-plaintext"
    assert [c[0] for c in mock_server.calls] == ["decrypt"]


def test_decrypt_propagates_500(mock_server):
    """500 from decrypt -> fail_json. Wrong ciphertext or revoked
    key both surface this way."""
    mock_server.on(
        "decrypt",
        raises=FakeApiException(status=500, body="key revoked"),
    )
    payload, code = mock_server.run_module(
        "decrypt.py",
        params={
            "key_name": "/keys/revoked",
            "ciphertext": "BLOB",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 1, payload


# ---------------------------------------------------------------------------
# Sign / Verify pair
# ---------------------------------------------------------------------------


def test_sign_returns_signature(mock_server):
    """sign action: call SignDataWithClassicKey -> return result."""
    mock_server.on(
        "sign_data_with_classic_key",
        response={"result": "ABCDEF_SIGNATURE"},
    )
    payload, code = mock_server.run_module(
        "sign_data_with_classic_key.py",
        params={
            "display_id": "abc",
            "message": "data-to-sign",
            "version": 1,
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    assert result.get("result") == "ABCDEF_SIGNATURE"


# ---------------------------------------------------------------------------
# UID action sanity: token rotation cycle
# ---------------------------------------------------------------------------


def test_uid_rotate_token_returns_new_token_verbatim(mock_server):
    """uid_rotate_token returns the new token verbatim under result.
    Contract (see tests/mock/test_uid_action.py for the rationale):
    the helper does NOT mask the token because chained tasks need
    it for follow-up calls (uid_create_child_token,
    uid_list_children). Playbook authors add `no_log: true` on the
    task itself for log-redaction."""
    mock_server.on(
        "uid_rotate_token",
        response={"token": "new-uid-token-after-rotation"},
    )
    payload, code = mock_server.run_module(
        "uid_rotate_token.py",
        params={
            "auth_method_name": "/auth/uid",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )
    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    assert result.get("token") == "new-uid-token-after-rotation", (
        f"UID rotate must return token verbatim for chaining; got {result!r}"
    )
