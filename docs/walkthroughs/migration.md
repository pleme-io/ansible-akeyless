# Migrate from another secrets manager

If you're moving from HashiCorp Vault, AWS Secrets Manager, or
Azure Key Vault to Akeyless, this walkthrough maps your existing
playbook patterns to the equivalent in `drzln0.akeyless`.

The good news: Akeyless's API + the standard Ansible lookup/module
shape means most migrations are search-and-replace rather than
rewrite-from-scratch.

## From HashiCorp Vault

### KV v2 read

```yaml
# Before (community.hashi_vault):
password: "{{ lookup('community.hashi_vault.vault_read',
              'secret/data/app/db', field='password') }}"

# After (drzln0.akeyless):
password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
```

Akeyless secret paths use `/` (forward-slash) like Vault but DON'T
need the `secret/data/` prefix. The lookup returns the value
directly (no `.data.data.password` walk).

### Dynamic DB credentials

```yaml
# Before (community.hashi_vault):
db_creds: "{{ lookup('community.hashi_vault.vault_read',
              'database/creds/readonly') }}"

# After (drzln0.akeyless):
db_creds: "{{ lookup('drzln0.akeyless.dynamic_secret',
              '/dynamic/db/readonly') }}"
```

Both return `{user, password}` dicts (Akeyless's shape varies by
producer type; see the [dynamic secrets walkthrough](dynamic-secrets.md)).

### PKI cert issuance

```yaml
# Before (community.hashi_vault):
cert: "{{ lookup('community.hashi_vault.vault_pki_generate_certificate',
                  role_name='web', engine_mount_point='pki',
                  common_name='web.example.com') }}"

# After (drzln0.akeyless):
cert: "{{ lookup('drzln0.akeyless.pki_certificate', '/pki/web',
                  common_name='web.example.com') }}"
```

Returns the same `{cert, private_key, ca_chain}` shape.

### Auth method config (Vault userpass → Akeyless access_key)

```yaml
# Before (hashivault):
- hashivault_userpass_create:
    name: app
    pass: "{{ app_password }}"

# After (Akeyless):
- drzln0.akeyless.auth_method_api_key:
    name: /auth/app
    state: present
```

Vault's userpass + Akeyless's `access_key` auth are structurally
similar but Akeyless issues an access_id + access_key pair (not a
username + password).

## From AWS Secrets Manager

### Secret read

```yaml
# Before (community.aws.secretsmanager_secret):
- ansible.builtin.set_fact:
    password: "{{ lookup('community.aws.aws_secret', 'app/db/password',
                          region='us-east-1') }}"

# After (drzln0.akeyless):
- ansible.builtin.set_fact:
    password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
```

Akeyless paths use `/`-separated namespaces; AWS uses arbitrary
strings. You'll typically reshape `app/db/password` →
`/app/db/password` (with the leading slash). No region needed —
Akeyless is region-agnostic to your gateway.

### Rotation policies

AWS's "automatic rotation" maps to Akeyless's `rotated_secret_*`
modules. The cron-style schedule becomes a `rotation_hour` +
`rotation_interval` pair:

```yaml
# Before (AWS): configured via Lambda + secrets manager rotation
# After:
- drzln0.akeyless.rotated_secret_postgresql:
    name: /rotated/db/app
    target_name: /targets/prod-db
    rotation_hour: 2
    rotation_interval: 30
    rotated_username: app
    state: present
```

See [Dynamic + rotated secrets](dynamic-secrets.md) for the full
configuration shape.

## From Azure Key Vault

### Secret read

```yaml
# Before (azure.azcollection):
- ansible.builtin.set_fact:
    password: "{{ lookup('azure.azcollection.azure_keyvault_secret',
                          'db-password',
                          vault_url='https://my-kv.vault.azure.net/') }}"

# After (drzln0.akeyless):
- ansible.builtin.set_fact:
    password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
```

### Certificate retrieval

```yaml
# Before (Azure):
- azure.azcollection.azure_rm_keyvaultsecret_info:
    name: webserver-cert
    vault_url: https://my-kv.vault.azure.net/

# After (Akeyless):
- ansible.builtin.set_fact:
    cert: "{{ lookup('drzln0.akeyless.pki_certificate',
              '/pki/webserver-issuer') }}"
```

## Bulk migration strategy

For a large codebase, the safest pattern is:

1. **Identify all secret references**: `grep -rn "vault_read\|aws_secret\|azure_keyvault" .`
2. **Map each path**: write a CSV with `(old_path, new_akeyless_path)`.
3. **Mirror secrets first**: write a one-shot playbook using the
   `drzln0.akeyless.static_secret` module to push every value from
   the old vault into Akeyless (idempotent — re-runs are safe).
4. **Swap one playbook at a time**: convert the lookups + verify in
   a non-prod environment.
5. **Keep both readers for a week**: a Python jq-style transformation
   on the lookups lets you switch the source dynamically:
   ```yaml
   password: "{{ lookup(akeyless_or_vault, path) }}"
   ```
   where `akeyless_or_vault` resolves to `drzln0.akeyless.secret`
   in newly migrated envs and `community.hashi_vault.vault_read`
   in legacy envs.
6. **Decommission old vault** once every consumer has migrated.

## Auth method equivalents

| Source | Akeyless equivalent |
|---|---|
| Vault Token | `token` auth-option (pre-issued) |
| Vault AppRole | `access_key` access type |
| Vault Kubernetes auth | `k8s` access type |
| Vault AWS IAM | `aws_iam` access type |
| AWS Secrets Manager IAM | `aws_iam` access type |
| Azure Key Vault MSI | `azure_ad` access type |

See [Authentication reference](../reference/authentication.md) for
the full table.

## Common gotchas

- **Path style**: Akeyless uses `/path/to/secret` everywhere (always
  leading slash). Vault paths look the same; AWS / Azure don't.
- **Value shape**: Akeyless `secret` lookup returns the raw string
  (no `.data.password` walk). Use `secret_to_json` if your value
  is a JSON blob.
- **Pre-issued tokens**: Akeyless and Vault tokens aren't compatible.
  You'll need to mint Akeyless credentials (access_id + access_key)
  separately and either store them in your CI secrets or use AWS
  IAM / K8s auth to bootstrap.
