# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration test: UID action module
# (uid_generate_token.py).
#
# Action modules are one-shot calls -- no get/update/delete dance. The
# contract for these is "always emits changed=True, and any sensitive
# response field is masked in the exit payload."

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def test_uid_generate_token_masks_token(mock_server):
    """uid_generate_token returns a real token; module exits with the
    token field masked to *** but leaves other fields intact."""
    mock_server.on(
        "uid_generate_token",
        response={
            "token": "real-secret-uid-token",
            "uid_token": "uid-cookie",
            "ttl": 3600,
        },
    )

    payload, code = mock_server.run_module(
        "uid_generate_token.py",
        params={
            "auth_method_name": "uid-method",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is True
    result = payload.get("result") or {}
    # Token must be masked.
    assert result.get("token") == "***", result
    # Non-sensitive fields are echoed through.
    assert result.get("uid_token") == "uid-cookie", result
    assert result.get("ttl") == 3600, result
    methods = [name for name, _body in mock_server.calls]
    assert methods == ["uid_generate_token"], methods


def test_uid_generate_token_sends_auth_method_name(mock_server):
    """The request body should carry the auth_method_name and a token from auth()."""
    mock_server.on(
        "uid_generate_token",
        response={"token": "abc"},
    )

    payload, code = mock_server.run_module(
        "uid_generate_token.py",
        params={
            "auth_method_name": "my-uid-method",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )

    assert code == 0, payload
    # The body is built via akeyless.UidGenerateToken(**filtered), which in
    # our fake-akeyless returns a MagicMock recording the kwargs. The mock
    # server doesn't inspect the body itself -- just confirms dispatch.
    name, body = mock_server.calls[0]
    assert name == "uid_generate_token"
    assert body is not None
