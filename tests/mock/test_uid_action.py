# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration test: UID action module
# (uid_generate_token.py).
#
# Action modules are one-shot calls -- no get/update/delete dance.
# The contract is "always emits changed=True and returns the SDK
# response verbatim under `result`". An earlier draft masked the
# token field server-side, but that turned out to be the wrong
# layer to redact at -- subsequent tasks (uid_rotate_token,
# uid_create_child_token) need the cleartext token to chain. The
# playbook author opts into log redaction with the standard Ansible
# `no_log: true` on the task, which keeps the value usable in
# downstream `vars: { ... }` while still keeping it out of any
# logged output.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def test_uid_generate_token_returns_token_verbatim(mock_server):
    """uid_generate_token returns the SDK token verbatim under
    result. Playbook authors add `no_log: true` to the task for
    redaction; the module must preserve the value so chained calls
    (rotate, child-token, list-children) can reference it."""
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
    # Token preserved verbatim so chained tasks can use it.
    assert result.get("token") == "real-secret-uid-token", result
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
