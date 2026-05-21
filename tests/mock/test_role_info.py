# Copyright: (c) 2026, pleme-io
# MIT License
#
# Mock-server integration test: read-only info module (role_info).
#
# Info modules wrap a single GET-style endpoint and exit with changed=False
# regardless of result content. They are the simplest mock-test shape and
# serve as the template for new <resource>_info modules.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def test_role_info_returns_data(mock_server):
    """role_info exits changed=False with the API response under .result."""
    mock_server.on(
        "get_role",
        response={"role_name": "demo", "rules": [{"path": "/secrets/*"}]},
    )

    payload, code = mock_server.run_module(
        "role_info.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    result = payload.get("result")
    assert result == {"role_name": "demo", "rules": [{"path": "/secrets/*"}]}


def test_role_info_handles_empty_payload(mock_server):
    """An empty dict response should still exit cleanly with result={}."""
    mock_server.on("get_role", response={})

    payload, code = mock_server.run_module(
        "role_info.py",
        params={
            "name": "demo",
            "access_id": "p-test",
            "access_key": "k-test",
        },
    )

    assert code == 0, payload
    assert payload.get("changed") is False
    assert payload.get("result") == {}
