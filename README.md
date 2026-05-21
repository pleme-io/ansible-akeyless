# akeyless.akeyless

> Auto-generated Ansible collection for Akeyless Vault — 208 modules covering the full V2 API surface, regenerated from upstream resource specs on every change.

[![CI](https://github.com/pleme-io/ansible-akeyless/actions/workflows/ci.yml/badge.svg)](https://github.com/pleme-io/ansible-akeyless/actions/workflows/ci.yml)
[![Release](https://github.com/pleme-io/ansible-akeyless/actions/workflows/release.yml/badge.svg)](https://github.com/pleme-io/ansible-akeyless/actions/workflows/release.yml)
[![Galaxy](https://img.shields.io/ansible/collection/v/akeyless/akeyless)](https://galaxy.ansible.com/akeyless/akeyless)
[![Downloads](https://img.shields.io/ansible/collection/d/akeyless/akeyless)](https://galaxy.ansible.com/akeyless/akeyless)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

> **Note.** This repo is a public mirror of
> [`ansible-akeyless-gen`](https://github.com/pleme-io/ansible-akeyless-gen);
> open issues and PRs upstream.

---

## What it is

`akeyless.akeyless` is an Ansible collection that exposes the entire
[Akeyless Vault](https://www.akeyless.io/) V2 API as native Ansible modules.
Each module is a thin Python wrapper around the official
[`akeyless`](https://pypi.org/project/akeyless/) Python SDK, with consistent
authentication, idempotency, sensitive-value masking, and check-mode support.

The collection is **not hand-written**. Every module — argument spec, docs
stub, return shape, SDK binding — is emitted from a TOML resource specification
in the upstream
[`akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources)
repository. The TOML specs are passed through the
[`iac-forge`](https://github.com/pleme-io/iac-forge) intermediate
representation and rendered by the
[`ansible-forge`](https://github.com/pleme-io/ansible-forge) backend.
Result: bug-for-bug parity with the upstream Terraform provider, and a single
place (the TOML spec) to fix anything that drifts.

This release covers **208 modules** across three shapes:

| Shape           | Count | Module pattern                              | Maps to                          |
|-----------------|-------|---------------------------------------------|----------------------------------|
| CRUD resource   | 157   | `state: present \| absent`                  | create / update / get / delete   |
| Data source     | 25    | `<resource>_info`                           | list / get endpoints (read-only) |
| RPC action      | 26    | one-shot call, `changed: true`              | crypto, UID tokens, syncs, etc.  |

PRM-1790 (Genuine Parts Co.) Universal Identity token operations land in
this release as first-class modules with sensitive-output masking on the
generated token.

---

## Quickstart

### 1. Install the Python SDK

```bash
pip install 'akeyless>=5.0.22'
```

### 2. Install the collection

```bash
ansible-galaxy collection install akeyless.akeyless
```

### 3. Configure credentials

Pick one auth path. Environment variables are read by every module:

```bash
# Access key auth (most common)
export AKEYLESS_ACCESS_ID='p-abcd1234'
export AKEYLESS_ACCESS_KEY='base64-encoded-key=='

# OR pre-issued token (skips auth call)
export AKEYLESS_TOKEN='t-...'

# Optional: point at a self-hosted gateway
export AKEYLESS_GATEWAY_URL='https://gateway.example.com'
```

Per-task params (`access_id`, `access_key`, `access_type`, `gateway_url`)
override env vars when present.

### 4. Run a playbook

```yaml
- hosts: localhost
  gather_facts: false
  collections: [akeyless.akeyless]
  tasks:
    - name: Create a static secret
      akeyless.akeyless.static_secret:
        name: /demo/hello
        value: world
        state: present
```

That's the full loop — no inventory, no hosts file required for management
plane work.

---

## Module categories

Module reference (will resolve once GitHub Pages is enabled):
<https://pleme-io.github.io/ansible-akeyless-gen/>

| Category                     | Count | Examples                                                 |
|------------------------------|-------|----------------------------------------------------------|
| [Auth methods](https://pleme-io.github.io/ansible-akeyless-gen/#auth-methods)             |    16 | `auth_method_api_key`, `auth_method_oidc`, `auth_method_universal_identity` |
| [Roles & policies](https://pleme-io.github.io/ansible-akeyless-gen/#roles)                |     4 | `role`, `role_assoc`, `role_rule`                        |
| [Static & dynamic secrets](https://pleme-io.github.io/ansible-akeyless-gen/#secrets)      |    33 | `static_secret`, `dynamic_secret_aws`, `dynamic_secret_k8s` |
| [Rotated secrets](https://pleme-io.github.io/ansible-akeyless-gen/#rotated-secrets)       |    23 | `rotated_secret_aws`, `rotated_secret_mysql`             |
| [Targets](https://pleme-io.github.io/ansible-akeyless-gen/#targets)                       |    29 | `target_aws`, `target_db`, `target_hashi_vault`          |
| [Crypto keys](https://pleme-io.github.io/ansible-akeyless-gen/#crypto)                    |     4 | `classic_key`, `dfc_key`, `pki_cert_issuer`              |
| [Gateway producers](https://pleme-io.github.io/ansible-akeyless-gen/#gateway-producers)   |    24 | `gateway_producer_aws`, `gateway_producer_postgresql`    |
| [Log forwarding](https://pleme-io.github.io/ansible-akeyless-gen/#log-forwarding)         |    10 | `gateway_log_forwarding_datadog`, `gateway_log_forwarding_splunk` |
| [Data sources `_info`](https://pleme-io.github.io/ansible-akeyless-gen/#info)             |    25 | `auth_methods_info`, `secret_value_info`, `roles_info`   |
| [RPC actions](https://pleme-io.github.io/ansible-akeyless-gen/#actions)                   |    26 | `encrypt`, `decrypt`, `uid_generate_token`, `certificate` |

Totals: **157 CRUD resources · 25 data sources · 26 RPC actions = 208 modules.**

---

## Authentication options

All access types supported by the Akeyless `auth` endpoint work uniformly.
Pick the one that fits your environment; the module surface is identical.

### Access key (default)

```yaml
- akeyless.akeyless.static_secret:
    name: /app/db/password
    value: '{{ generated_password }}'
    access_id:   '{{ akeyless_access_id }}'
    access_key:  '{{ akeyless_access_key }}'
    access_type: access_key
```

### Other auth types

Pass `access_type` to switch — the SDK handles the dance for you.

- `access_type: api_key` — legacy API key auth.
- `access_type: k8s` — Kubernetes ServiceAccount token auth (gateway derives identity).
- `access_type: aws_iam` — STS-signed IAM auth from EC2 / Lambda.
- `access_type: azure_ad` — Azure AD managed identity auth.
- `access_type: gcp` — GCP IAM auth.
- `access_type: universal_identity` — UID auth (works with the PRM-1790 token modules).
- `access_type: jwt` / `oidc` / `saml` / `ldap` / `cert` / `oci` / `oauth2` / `email` / `huawei` / `kerberos`.

Or skip auth entirely and pass an already-issued token via `AKEYLESS_TOKEN`.

---

## Examples

End-to-end playbooks live under [`examples/`](./examples/):

- `examples/static_secret.yml`             — CRUD on a static secret
- `examples/dynamic_secret_aws.yml`        — AWS producer + credential issuance
- `examples/role_and_auth_method.yml`      — API-key auth method, role, association, rules
- `examples/uid_token_lifecycle.yml`       — UID auth method + token gen/rotate/revoke (PRM-1790)
- `examples/certificate_provision.yml`     — issue a certificate via the action module
- `examples/rotated_secret_with_target.yml` — target + rotated secret + manual rotation
- `examples/check_mode_demo.yml`           — exercise `--check` for diff-only runs

See [`examples/README.md`](./examples/README.md) for an indexed walkthrough.

---

## Generator pipeline

This collection is **not hand-maintained**. The full pipeline:

```
akeyless-terraform-resources/resources/*.toml   ← spec source
  → iac-forge ResourceSpec parser
  → iac-forge IR (IacResource / IacAction / IacDataSource)
  → ansible-forge AnsibleBackend
  → plugins/modules/*.py + plugins/module_utils/akeyless_client.py + galaxy.yml
  → ansible-galaxy collection build
  → galaxy.ansible.com
```

To change a module:

1. **Missing endpoint?** Open an issue using the
   [`Missing endpoint`](./.github/ISSUE_TEMPLATE/missing-endpoint.yml) template
   here, or send a PR to
   [`akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources)
   adding a TOML spec under `resources/`.
2. **Generator bug?** Open a bug report here; if the fix is in the emitter,
   it'll get patched in [`ansible-forge`](https://github.com/pleme-io/ansible-forge)
   and a re-generation lands as a follow-up commit.
3. **Docs / examples / tests?** Send a PR directly to this repo — those are
   the hand-maintained pieces.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full flow.

---

## Compatibility

| Component   | Supported            |
|-------------|----------------------|
| Ansible     | `>= 2.14.0`          |
| Python      | `>= 3.10`            |
| Akeyless SDK | `akeyless >= 5.0.22` |
| Platforms   | Any control node that runs Ansible; modules call the Akeyless API over HTTPS. |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). TL;DR: file an issue first, point
patches at the spec source (`akeyless-terraform-resources`) or the emitter
(`ansible-forge`) rather than at generated module files.

We follow the [Contributor Covenant 2.1](./CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](./SECURITY.md). Use GitHub's **Private vulnerability
reporting** to disclose; please don't open public issues for security bugs.

## License

[MIT](./LICENSE). Copyright (c) 2026 pleme-io.
