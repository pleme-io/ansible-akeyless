# Live-coverage known issues

Loose ends the matrix correctly classifies as API_REJECTED but that
deserve explicit documentation so the next reader doesn't re-debug
them. Run `nix run .#live-coverage-gateway` for the matrix itself.

## Upstream `akeyless` Python SDK URL drift

Five modules dispatch correctly and the SDK call is well-formed, but
the URL the SDK posts to has drifted from what the Akeyless API
currently serves. These can't be fixed in our module — the path is
baked into the SDK's generated client. Bug reports / SDK upgrade are
the only routes.

| module | SDK posts to | API expects |
|---|---|---|
| `groups_info.py` | `/list-group` | `/list-groups` |
| `gateway_producer_redis.py` | `/gateway-create-producer-Redis` | `/gateway-create-producer-redis` |
| `auth_method_huawei.py` | `/create-auth-method-huawei` | (endpoint removed / never existed) |
| `kmip_environment.py` | `/kmip-create-environment` | (renamed; modern name TBD) |
| `kmip_environment_v2.py` | `/kmip-create-environment` | (same as above) |

Verified via:
```
grep "'/list-group'" .venv/lib/python3.13/site-packages/akeyless/api/v2_api.py
# → confirms the SDK hard-codes the wrong path
```

## Auth-method creation requires elevated dev creds (403 AccessForbidden)

Seven modules need an admin-tier access ID with the
`auth_method_create` capability. The dev access ID in
`pleme-io/nix/secrets.yaml` lacks this, so live-coverage sees them as
API_REJECTED with `Status 403 Forbidden, Error: AccessForbidden`.

These would all WORKS the moment we route the test through an
admin-scoped access ID:

- `auth_method_api_key.py`
- `auth_method_aws_iam.py`
- `auth_method_azure_ad.py`
- `auth_method_k8s.py`
- `auth_method_ldap.py`
- `auth_method_oci.py`
- `auth_method_universal_identity.py`

The same permission gate keeps the fixture orchestrator from auto-
creating an `api_key_auth_method` / `uid_auth_method` fixture, so
the following NEEDS_PREREQ modules also stay blocked until the
admin-tier creds land:
- `auth_method_info.py` (needs the api_key auth method fixture)
- `role_auth_method_assoc.py` (needs the auth method + role)
- `uid_generate_token.py` (needs the UID auth method)

## Gateway-only modules without a fully-configured backend (~94)

`dynamic_secret_*` / `rotated_secret_*` / `gateway_producer_*` are
mostly gateway-bound. The gateway from `nix run .#live-coverage-
gateway` unlocks their dispatch + request-shape validation but can't
actually *create* them end-to-end against the dev account — most need
real backing infra (a real Postgres instance, real AWS IAM, real
Akeyless cluster id, etc.). The "API_REJECTED" classification here is
honest: the API saw the create call and rejected it for missing real
backend state, not for any flaw in our module.

## DB-probe hang (`dynamic_secret_redis.py`)

The gateway's redis-backend probe hangs far past any reasonable
client-side timeout (probe retries internally, holding the request
socket open). pytest-timeout kills our HTTP call, but the gateway
keeps the socket half-open; subsequent tests on the same connection
pool get ConnectionReset cascades that mis-classify the rest of the
run. Skipped in `coverage_matrix.py` until the gateway adds a
redis-probe timeout or we add per-test SDK-client isolation.

`dynamic_secret_mongodb` / `gateway_producer_mongo` exhibit a similar
but bounded variant — the gateway returns `failed to initialize DB
connection` after ~30s. These are correctly classified as
API_REJECTED (the API responded; it just refused).
