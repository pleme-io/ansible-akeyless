# `drzln0.akeyless` — Full-service Ansible integration for Akeyless Vault

Auto-generated Ansible Collection wrapping the entire Akeyless V2 API,
plus hand-tuned lookup / inventory / filter / test / callback / action /
cache plugins and ready-to-use roles. 209 modules at 100% V2 SDK method
coverage.

## Install

```bash
ansible-galaxy collection install drzln0.akeyless
```

## What ships

| Content | Count | Where |
|---|---|---|
| Modules (CRUD, action, info) | **209** | `plugins/modules/` |
| Lookup plugins | 3 | `plugins/lookup/{secret,dynamic_secret,pki_certificate}.py` |
| Inventory plugin | 1 | `plugins/inventory/akeyless.py` |
| Filter plugins | 7 | `plugins/filter/akeyless.py` |
| Test plugins | 4 | `plugins/test/{is_akeyless_path,is_akeyless_access_id,is_pem_block,is_base64}.py` |
| Callback plugin | 1 | `plugins/callback/akeyless_redactor.py` (secret redaction) |
| Action plugin | 1 | `plugins/action/secret_to_file.py` (atomic write) |
| Cache plugin | 1 | `plugins/cache/akeyless_token.py` (file-backed token cache) |
| Roles | 2 | `roles/akeyless_bootstrap/`, `roles/akeyless_install_certificate/` |
| Playbooks | 2 | `playbooks/{fetch_secrets_into_env_file,install_certificate_with_defaults}.yml` |
| Doc fragments | 1 | `plugins/doc_fragments/auth.py` (shared auth options) |
| Module utils | 2 | `plugins/module_utils/{akeyless_client,akeyless_lookup_auth}.py` |
| Action groups | 1 | `meta/runtime.yml` `action_groups.all` (set auth once via `module_defaults: group/drzln0.akeyless.all:`) |

## Quick starts

### Fetch a secret via lookup

```yaml
- name: Connect to DB
  community.mysql.mysql_db:
    login_password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"

- name: Fetch a fresh dynamic-secret credential
  ansible.builtin.set_fact:
    db_creds: "{{ lookup('drzln0.akeyless.dynamic_secret', '/dynamic/db/admin') }}"

- name: Materialise a PKI cert from Akeyless
  ansible.builtin.set_fact:
    cert_bundle: "{{ lookup('drzln0.akeyless.pki_certificate', '/pki/web',
                            common_name='web.example.com') }}"
```

### Manage an Akeyless resource via a module

```yaml
- name: Ensure role exists
  drzln0.akeyless.role:
    state: present
    name: "{{ role_name }}"
    description: "Managed by ansible"

- name: Attach an auth method to the role
  drzln0.akeyless.role_auth_method_assoc:
    state: present
    role_name: "{{ role_name }}"
    am_name: "{{ auth_method_name }}"
```

### Treat Akeyless as your inventory source

`inventory.akeyless.yml`:

```yaml
plugin: drzln0.akeyless.akeyless
secrets:
  - /platform/prod/inventory   # stored as a JSON-shaped secret
```

The plugin loads JSON-shaped secrets of the form
`{hosts: {name: {vars}}, groups: {name: {hosts: [], vars: {}}}}` into the
inventory tree so playbooks reference values via standard
`host_vars` / `group_vars` without per-task lookup boilerplate.

### Use the bootstrap role

```yaml
- hosts: web
  roles:
    - role: drzln0.akeyless.akeyless_bootstrap
      vars:
        akeyless_bootstrap_secrets:
          - /platform/prod/db/password
          - /platform/prod/api/jwt-key
  # akeyless_secrets is now {password: ..., jwt-key: ...} on every host
```

### Install a certificate (and matching key)

```yaml
- hosts: nginx
  roles:
    - role: drzln0.akeyless.akeyless_install_certificate
      vars:
        akeyless_install_certificate_cert_secret: /pki/web/cert
        akeyless_install_certificate_key_secret: /pki/web/key
        akeyless_install_certificate_cert_path: /etc/nginx/ssl/web.crt
        akeyless_install_certificate_key_path: /etc/nginx/ssl/web.key
        akeyless_install_certificate_notify: "reload nginx"
```

### Transform secret payloads with filters

```yaml
# Parse a dotenv-formatted secret into an environment block
- name: Run app with secrets-from-vault env
  ansible.builtin.command: ./app
  environment: "{{ lookup('drzln0.akeyless.secret', '/app/.env')
                   | drzln0.akeyless.parse_dotenv_secret }}"

# Split a CA bundle into individual PEM blocks
- name: Install each trust root separately
  ansible.builtin.copy:
    content: "{{ item }}"
    dest: "/etc/ssl/certs/akeyless-{{ index }}.pem"
  loop: "{{ lookup('drzln0.akeyless.secret', '/ca/bundle')
            | drzln0.akeyless.split_pem_bundle }}"
  loop_control:
    index_var: index
```

Available filters: `b64decode_secret`, `parse_dotenv_secret`,
`secret_to_json`, `split_pem_bundle`, `secret_keys_to_env`,
`mask_secret`, `secret_strength`.

### Branch on content shape with tests

```yaml
- name: Verify access_id format before auth
  ansible.builtin.assert:
    that: lookup('env', 'AKEYLESS_ACCESS_ID')
          is drzln0.akeyless.is_akeyless_access_id

- name: Decode only when value is base64
  ansible.builtin.set_fact:
    decoded: "{{ secret | drzln0.akeyless.b64decode_secret
                 if secret is drzln0.akeyless.is_base64
                 else secret }}"
```

Available tests: `is_akeyless_path`, `is_akeyless_access_id`,
`is_pem_block`, `is_base64`.

### Skip per-task auth via the token cache

Across a large playbook each Akeyless call costs a fresh authentication
round-trip. Wire the `akeyless_token` cache plugin in `ansible.cfg` to
share a token across tasks / plays:

```ini
[defaults]
fact_caching = drzln0.akeyless.akeyless_token
fact_caching_connection = /var/cache/ansible/akeyless
fact_caching_timeout = 1500
```

File-backed (0600 perms, atomic writes, per-tenant keying by
`(gateway_url, access_id)`). Default TTL is 25 minutes — leaves
~35 minutes headroom on Akeyless's 60-minute token lifetime.

### Set Akeyless auth once via action_groups

`meta/runtime.yml` ships `action_groups.all` listing every module, so
you can set Akeyless auth on every task at once via `module_defaults`:

```yaml
- hosts: vault_clients
  module_defaults:
    group/drzln0.akeyless.all:
      gateway_url: "{{ akeyless_gateway_url }}"
      access_id: "{{ akeyless_access_id }}"
      access_key: "{{ akeyless_access_key }}"
  tasks:
    - drzln0.akeyless.role: { name: app-readonly, state: present }
    - drzln0.akeyless.static_secret: { name: /app/key, value: "..." }
```

## Authentication

The lookup, inventory plugin, role tasks, and every module accept the
standard set of auth options. Each falls back to its `AKEYLESS_*`
environment variable.

| Option / env var | Default |
|---|---|
| `gateway_url` / `AKEYLESS_GATEWAY_URL` | `https://api.akeyless.io` |
| `access_id` / `AKEYLESS_ACCESS_ID` | (required) |
| `access_key` / `AKEYLESS_ACCESS_KEY` | (required for `access_key` type) |
| `access_type` / `AKEYLESS_ACCESS_TYPE` | `access_key` |
| `token` / `AKEYLESS_TOKEN` | (skips auth call when set) |

## Architecture (load-bearing)

The collection is generated by [`ansible-forge`](https://github.com/pleme-io/ansible-forge)
reading TOML specs from
[`akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources).
Modules don't carry boilerplate — each declares an `argument_spec` dict
and delegates to one of three lifecycle helpers
(`run_standard_crud`, `run_action_module`, `run_info_module`) in
`plugins/module_utils/akeyless_client.py`. The helper module exports a
typed public API (`AkeylessConfig`, `AkeylessError` hierarchy,
`HttpStatus` enum, `SdkCall` NamedTuple, `@lifecycle_helper`,
`@requires_sdk` decorators) for advanced callers.

A regen-vs-collection backstop in `ansible-forge` enforces structural
equivalence between the generator output and the live collection on
every PR — the next `iac-forge generate --backend ansible` produces
the same shape that ships.

## Test pyramid

`nix flake check` runs:
- **smoke** — AST sweep, 100% V2 SDK method coverage
- **unit** — module shape, load, license header, YAML block, lifecycle
  helper behaviour, property tests, public API pinning
- **mock** — SDK-mocked module main() invocations
- **sanity** — galaxy.yml + meta + doc fragments + playbook YAML
- **openapi** — live OpenAPI coverage check

Plus dedicated CI workflows: ansible-test sanity, CodeQL, docs-lint,
matrix coverage (Py 3.10/3.11/3.12/3.13), ansible-lint
(playbooks/ + roles/), integration-live (real gateway), published-install.

Current test count: **5890+ passing** (1500+ via Hypothesis property
strategies).

## Versioning

`v0.x` is pre-1.0; module names, argspecs, and return shapes may change
as the upstream OpenAPI spec evolves. Pin in `requirements.yml`:

```yaml
collections:
  - name: drzln0.akeyless
    version: '>=0.2,<0.3'
```

After `v1.0`, breaking changes only in major bumps.

## License

GPL-3.0-or-later (per-module headers, matching ansible-core's runtime
license). Collection-level metadata in `galaxy.yml` lists MIT for the
overall project; the modules carry GPL3 individually as Galaxy
convention.
