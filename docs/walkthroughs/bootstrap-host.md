# Bootstrap a host with secrets — the `akeyless_bootstrap` role

The `akeyless_bootstrap` role fans an arbitrary list of secret paths
into a host-local fact dict (`akeyless_secrets`). Subsequent tasks
reference values via the standard Ansible idiom rather than per-task
lookup boilerplate.

## When to use it

- You have a host that needs many secrets at the start of a play
  (database password, API tokens, signing keys, certs).
- You want to keep secret resolution in ONE block at the top of the
  play so the rest of the playbook reads like normal Ansible.
- You want each host's secrets resolved against its own Akeyless
  tenant (different hosts can have different credentials).

## Minimum playbook

```yaml
- hosts: web
  roles:
    - role: drzln0.akeyless.akeyless_bootstrap
      vars:
        akeyless_bootstrap_secrets:
          - /platform/prod/db/password
          - /platform/prod/api/jwt-key
          - /platform/prod/redis/auth-token

  tasks:
    # `akeyless_secrets` is now defined on every host with:
    #   {"password": "...", "jwt-key": "...", "auth-token": "..."}
    - ansible.builtin.debug:
        msg: "DB password starts with: {{ akeyless_secrets.password[:4] }}***"
```

The role:
1. Authenticates once per host using the standard auth options
   (env vars or playbook-level vars).
2. Calls the `secret` lookup with all paths in a single batch
   request.
3. Sets `akeyless_secrets` as a host-local fact, keyed by the
   secret's basename (`/platform/prod/db/password` → key
   `password`).
4. Sets `no_log: true` so the resolved values never leak to stdout.

## Custom key mapping

Sometimes two secrets have the same basename. Override with a dict:

```yaml
- hosts: web
  roles:
    - role: drzln0.akeyless.akeyless_bootstrap
      vars:
        akeyless_bootstrap_secrets:
          db_password: /platform/prod/db/password
          jwt_signing: /platform/prod/api/jwt-key
          # Two `auth-token` secrets disambiguated:
          internal_token: /platform/internal/auth-token
          external_token: /platform/external/auth-token
```

`akeyless_secrets.db_password`, `akeyless_secrets.jwt_signing`, etc.

## Use with environment overrides

Real playbooks usually parameterise the secret paths per environment:

```yaml
- hosts: web
  vars:
    akeyless_env: "{{ inventory_environment }}"

  roles:
    - role: drzln0.akeyless.akeyless_bootstrap
      vars:
        akeyless_bootstrap_secrets:
          db_password: "/platform/{{ akeyless_env }}/db/password"
          api_key: "/platform/{{ akeyless_env }}/api/key"
```

## Composing with the cache plugin

When you wire the `akeyless_token` cache plugin (see
[Skip per-task auth](token-caching.md)), the role's auth call is
served from the cache after the first host. For a 50-host playbook,
that's 49 fewer auth round-trips per run.

## What's inside the role

`roles/akeyless_bootstrap/tasks/main.yml`:

```yaml
- name: Resolve secrets via Akeyless lookup
  ansible.builtin.set_fact:
    akeyless_secrets: >-
      {{ akeyless_bootstrap_secrets
         | drzln0.akeyless.secret_keys_to_dict
         | combine(_akeyless_resolved_pairs) }}
  vars:
    _akeyless_resolved_pairs: "{{ ... }}"
  no_log: true
```

(Simplified; see `roles/akeyless_bootstrap/tasks/main.yml` for the
real implementation.)

## Next: also install a TLS cert

[Install a TLS certificate](install-tls-cert.md) walks through the
sibling role `akeyless_install_certificate` for the common
"materialise a cert + key onto a host" workflow.
