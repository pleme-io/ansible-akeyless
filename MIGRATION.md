# Migration guide

Coming from another way of integrating Akeyless with Ansible? This file maps the most common patterns to their `drzln0.akeyless` equivalents.

## From the Akeyless CLI (`akeyless`)

The `akeyless` CLI is the reference admin tool. If you've been driving it from `ansible.builtin.command` / `shell` tasks, you can usually replace those with native modules.

| `akeyless` CLI | Ansible module |
|---|---|
| `akeyless create-role --name X` | `drzln0.akeyless.role` (`state: present`) |
| `akeyless update-role --name X --description Y` | `drzln0.akeyless.role` (idempotent — module diffs the live state and only updates on drift) |
| `akeyless delete-role --name X` | `drzln0.akeyless.role` (`state: absent`) |
| `akeyless assoc-role-am --role-name R --am-name A` | `drzln0.akeyless.role_assoc` (`state: present`) |
| `akeyless set-role-rule --role-name R --path P --capability read` | `drzln0.akeyless.role_rule` |
| `akeyless auth-method create-api-key --name X` | `drzln0.akeyless.auth_method_api_key` |
| `akeyless uid-generate-token --auth-method-name A` | `drzln0.akeyless.uid_generate_token` (action module) |
| `akeyless get-secret-value --name X` | `{{ lookup('drzln0.akeyless.secret', 'X') }}` (inline lookup) |
| `akeyless create-secret --name X --value Y` | `drzln0.akeyless.static_secret` |
| `akeyless encrypt --display-id K --plaintext P` | `drzln0.akeyless.encrypt` (action module) |

**Why prefer modules over `command:`**

- Idempotency: modules read current state and only apply changes on drift; `command:` always reports `changed`.
- `check_mode` support: modules respect `--check` for diff-only runs; shell tasks can't simulate.
- Sensitive value masking: modules wrap secret response fields with `no_log: true`; shell `register:` leaks to logs.
- Auth: modules reuse a single shared auth helper (`module_utils/akeyless_client.py`) — env vars work uniformly.

## From the official Akeyless Terraform provider

The Terraform provider `akeyless/akeyless` and this collection are generated from the same upstream resource specs, so the resource → module mapping is 1:1 with prefix-strip:

| Terraform resource | Ansible module |
|---|---|
| `akeyless_static_secret` | `drzln0.akeyless.static_secret` |
| `akeyless_role` | `drzln0.akeyless.role` |
| `akeyless_auth_method_api_key` | `drzln0.akeyless.auth_method_api_key` |
| `akeyless_target_aws` | `drzln0.akeyless.target_aws` |
| `akeyless_dynamic_secret_aws` | `drzln0.akeyless.dynamic_secret_aws` |
| `akeyless_rotated_secret_postgresql` | `drzln0.akeyless.rotated_secret_postgresql` |
| `akeyless_pki_cert_issuer` | `drzln0.akeyless.pki_cert_issuer` |
| `akeyless_classic_key`, `akeyless_dfc_key` | `drzln0.akeyless.classic_key`, `drzln0.akeyless.dfc_key` |
| `akeyless_kmip_client`, `akeyless_kmip_environment` | `drzln0.akeyless.kmip_client`, `drzln0.akeyless.kmip_environment` |

Field names are the same modulo `kebab-case` → `snake_case`.

## From custom shell scripts hitting the API

If you've been `curl`-ing `https://api.akeyless.io/auth` and `/get-secret-value`, the lookup plugin replaces the whole script:

```yaml
- name: Old way (shell)
  ansible.builtin.shell: |
    TOKEN=$(curl -s https://api.akeyless.io/auth -d ...)
    curl -s https://api.akeyless.io/get-secret-value -d "{...}"
  register: secret
  no_log: true

- name: New way (lookup)
  ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/path/to/secret') }}"
```

The lookup handles auth, single-request batching, and result ordering. One line, no `register`, no `no_log` boilerplate.

## Authentication options

All Akeyless auth types work uniformly. Set `access_type` on the module/lookup OR via env:

```bash
export AKEYLESS_ACCESS_ID='p-xxx'
export AKEYLESS_ACCESS_KEY='base64=='
export AKEYLESS_ACCESS_TYPE='access_key'   # default; or api_key, aws_iam, azure_ad, k8s, oidc, jwt, etc.
```

For workloads inside a cluster, use `access_type: k8s` and the gateway picks up the ServiceAccount token automatically. For EC2/Lambda, `access_type: aws_iam` uses STS signing.

For ephemeral or pre-issued tokens, set `AKEYLESS_TOKEN` and the auth call is skipped.

## When the upstream API changes

This collection is regenerated from `pleme-io/akeyless-terraform-resources` whenever the OpenAPI spec moves. A new API endpoint usually means:

1. Spec change merged in `akeyless-terraform-resources`
2. Regenerate via `iac-forge generate --backend ansible`
3. New module appears in `plugins/modules/`
4. Tag + ship a new collection version

If you need an endpoint that isn't yet covered, file a [Missing endpoint](.github/ISSUE_TEMPLATE/missing-endpoint.yml) issue.

## Backwards compatibility

`v0.x` is pre-1.0; module names, argspecs, and return shapes may change as the upstream OpenAPI spec evolves and as we tune what the generator emits. Pin the collection version in `requirements.yml` until `v1.0`:

```yaml
# requirements.yml
collections:
  - name: drzln0.akeyless
    version: '==0.2.0'
```

After `v1.0`, the SemVer contract holds: breaking changes only in major versions.
