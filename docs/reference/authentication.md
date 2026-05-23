# Authentication reference

Every module, lookup, inventory plugin, and action plugin in this
collection takes the same set of auth options. They're documented
here once.

## The five auth options

| Option | Env var | Default |
|---|---|---|
| `gateway_url` | `AKEYLESS_GATEWAY_URL` | `https://api.akeyless.io` |
| `access_id` | `AKEYLESS_ACCESS_ID` | — (required unless `token` is set) |
| `access_key` | `AKEYLESS_ACCESS_KEY` | — (required for `access_key` access type) |
| `access_type` | `AKEYLESS_ACCESS_TYPE` | `access_key` |
| `token` | `AKEYLESS_TOKEN` | — (skips the auth call when set) |

## Precedence

For each field, the auth resolution picks in this order:

1. Explicit task arg (e.g. `access_id: p-abc` on the task).
2. Playbook-level `vars:` block.
3. `module_defaults: group/drzln0.akeyless.all:` (see
   [Auth once per play](../walkthroughs/module-defaults.md)).
4. Environment variable.
5. Built-in default.

## Access types

`access_type` selects the Akeyless auth method. Supported values
mirror Akeyless's CLI:

- `access_key` (default) — username/password style. Requires
  `access_id` + `access_key`.
- `api_key` — same as `access_key` for our purposes; some Akeyless
  docs call the same flow `api_key`.
- `aws_iam` — IAM-based auth. Requires `access_id`; AWS credentials
  are picked up from the standard env (boto3 chain).
- `gcp` — GCE / GKE service account. Requires `access_id`.
- `azure_ad` — Azure AD. Requires `access_id` + an Azure-AD-issued
  client assertion.
- `k8s` — Kubernetes Service Account. Auto-discovers the in-pod SA
  token; needs `access_id` of the K8s auth method.
- `oidc` — generic OIDC. Triggers a browser flow on the controller.
- `cert` — mTLS. Requires `access_id` + cert/key supplied via
  `cert_data` / `key_data`.

For most automation, `access_key` (with `access_id` + `access_key`
from env / vault / AAP credentials) is the path. The other access
types are for specific deployment contexts (running inside AWS, on
GKE, etc).

## Pre-issued tokens

If you already have a valid token (e.g. you called
`uid_generate_token` in an earlier task), set `token=...` and the
helper skips the auth round-trip entirely:

```yaml
- name: Get a UID token
  drzln0.akeyless.uid_generate_token:
    auth_method_name: /auth/uid
    access_id: p-uid-bootstrap
    access_key: "{{ uid_bootstrap_key }}"
  register: uid_result

- name: Use the issued token for downstream calls
  drzln0.akeyless.static_secret:
    name: /app/secret
    value: rotated
    state: present
    token: "{{ uid_result.result.token }}"
```

## With the cache plugin

When the `akeyless_token` cache plugin is wired (see
[Skip per-task auth](../walkthroughs/token-caching.md)), the cached
token effectively becomes the `token` for every subsequent call
within the TTL window. You don't need to set `token` explicitly —
the cache plugin handles it.

## With `module_defaults`

Most playbooks should set auth once at the top of the play:

```yaml
- hosts: vault_clients
  module_defaults:
    group/drzln0.akeyless.all:
      gateway_url: "{{ akeyless_gateway_url }}"
      access_id: "{{ akeyless_access_id }}"
      access_key: "{{ akeyless_access_key }}"
```

`group/drzln0.akeyless.all:` is registered in `meta/runtime.yml` and
lists all 209 modules. Every task inherits the defaults without
needing to repeat them.

## Lookup-specific notes

The three lookup plugins (`secret`, `dynamic_secret`,
`pki_certificate`) accept auth options as either kwargs OR via env:

```yaml
# kwarg form
- ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/x',
                     gateway_url='https://my-gw.example.com',
                     access_id='p-abc',
                     access_key='k-xyz') }}"

# env form (most common)
- ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/x') }}"
  # auth fields come from AKEYLESS_* env vars
```

Lookups DO NOT inherit `module_defaults` — that mechanism applies to
modules only. For lookups, use env vars or explicit kwargs.

## Inventory plugin notes

The inventory plugin reads its auth options from environment
variables (per Ansible inventory plugin convention). For AWX/AAP,
set them via the inventory source's credential binding — see
[AWX / AAP integration](../walkthroughs/awx-aap-integration.md).
