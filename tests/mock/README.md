# Mock-server integration tests

End-to-end module tests that exercise the full `main()` flow -- argspec
resolution, auth dispatch, SDK call, response handling, exit_json payload
-- against a stubbed Akeyless API. No live tenant required.

## Why a mock SDK and not `responses` / `aresponses`?

The `akeyless` Python SDK is OpenAPI-generated. Its request layer does
client-side body validation against generated model classes *before* a
real HTTP request is sent, so HTTP-layer interceptors (`responses`,
`requests-mock`, `aresponses`) don't see the call -- the SDK fails earlier
with `TypeError: __init__() got an unexpected keyword argument` if your
mock fixture doesn't match the exact model contract.

We sidestep that by replacing `akeyless.V2Api` with a `MockServer`-backed
proxy: calls to `client.<method>(body)` route through `MockServer._dispatch`,
which is the same fallback recommended in
[`tests/unit/plugins/modules/test_module_behavior.py`](../unit/plugins/modules/test_module_behavior.py).

## Pattern

```python
def test_my_module(mock_server):
    mock_server.on("create_role", response={"role_name": "demo"})
    mock_server.on("get_role", raises=FakeApiException(status=404, body="missing"))

    payload, code = mock_server.run_module(
        "role.py",
        params={"name": "demo", "access_id": "p", "access_key": "k", "state": "present"},
    )

    assert code == 0
    assert payload["changed"] is True
    assert [name for name, _body in mock_server.calls] == ["get_role", "create_role"]
```

The fixture (`mock_server`) is in `conftest.py`. Each test gets a fresh
instance and `sys.modules` is restored on teardown.

## Adding a new test

1. **Pick a module** under `plugins/modules/`. Read its `main()` to learn
   which V2Api methods it calls (look for `call_api(..., "<method_name>", ...)`).
2. **Register stub responses** for each method via `mock_server.on(name, response={...})`
   or `mock_server.on(name, raises=FakeApiException(status=...))`.
3. **Call** `mock_server.run_module("<filename>.py", params={...})`. The
   helper returns `(exit_kwargs, exit_code)`.
4. **Assert** on the payload (`changed`, `result`, sensitive masking, etc.)
   and on `mock_server.calls` (the recorded `[(method_name, body), ...]`
   sequence) for dispatch contract.

## Scope

Three tests ship as proof of pattern:

| File                          | Module                  | Shape          |
|-------------------------------|-------------------------|----------------|
| `test_role_lifecycle.py`      | `role.py`               | CRUD           |
| `test_role_info.py`           | `role_info.py`          | data source    |
| `test_uid_action.py`          | `uid_generate_token.py` | RPC action     |

Add more as needed -- the cost is one `mock_server.on(...)` per endpoint
and one assertion per behaviour bullet.
