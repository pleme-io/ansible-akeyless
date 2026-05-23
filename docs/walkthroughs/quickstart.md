# Quickstart — your first secret fetch

This walkthrough takes you from "I just installed the collection" to
"my playbook reads a secret from Akeyless" in under five minutes.

## Prerequisites

- An Akeyless tenant + an [access ID](https://docs.akeyless.io/docs/access-keys)
  with read permission on at least one secret.
- A Python environment with ansible-core ≥ 2.14 and the Akeyless SDK:
  ```bash
  pip install 'ansible-core>=2.14' 'akeyless>=5.0.22'
  ```

## Install the collection

```bash
ansible-galaxy collection install drzln0.akeyless
```

Or pin a version range in `requirements.yml`:

```yaml
collections:
  - name: drzln0.akeyless
    version: '>=0.2,<0.3'
```

## Fetch a secret via the `secret` lookup

The simplest possible playbook:

```yaml
- hosts: localhost
  tasks:
    - name: Print a secret from Akeyless
      ansible.builtin.debug:
        msg: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
      vars:
        ansible_akeyless_access_id: p-abc123
        ansible_akeyless_access_key: "{{ lookup('env', 'AKEYLESS_ACCESS_KEY') }}"
```

Run it:

```bash
ANSIBLE_AKEYLESS_ACCESS_ID=p-abc123 \
ANSIBLE_AKEYLESS_ACCESS_KEY=<your-access-key> \
  ansible-playbook quickstart.yml
```

## Auth precedence

The lookup picks credentials in this order (per field):

1. Explicit lookup kwargs: `lookup('drzln0.akeyless.secret', '/x', access_id='p-...', access_key='...')`
2. Playbook-level `vars:` (the example above)
3. Environment variables: `AKEYLESS_GATEWAY_URL`, `AKEYLESS_ACCESS_ID`,
   `AKEYLESS_ACCESS_KEY`, `AKEYLESS_ACCESS_TYPE`, `AKEYLESS_TOKEN`.
4. Built-in defaults (gateway URL → `https://api.akeyless.io`, access
   type → `access_key`).

If you set `token=<...>` (either as a lookup kwarg or via
`AKEYLESS_TOKEN`), the lookup short-circuits the auth round-trip and
uses your pre-issued token directly.

See the [Authentication reference](../reference/authentication.md) for
the full table.

## Fetch many secrets in one call

The lookup batches: passing N terms makes one API call and returns N
values aligned to input order.

```yaml
- ansible.builtin.set_fact:
    db_user: "{{ creds[0] }}"
    db_pass: "{{ creds[1] }}"
  vars:
    creds: "{{ lookup('drzln0.akeyless.secret',
                      '/app/db/user',
                      '/app/db/password') }}"
```

## Use the value in a real task

Most modules accept variables directly. For database connections:

```yaml
- community.mysql.mysql_db:
    name: appdb
    state: present
    login_user: "{{ lookup('drzln0.akeyless.secret', '/app/db/user') }}"
    login_password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
```

Add `no_log: true` on the task to keep the resolved values out of your
ansible log output:

```yaml
- community.mysql.mysql_db:
    name: appdb
    login_user: "{{ lookup('drzln0.akeyless.secret', '/app/db/user') }}"
    login_password: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"
  no_log: true
```

## Next steps

- **[Auth once per play](module-defaults.md)**: avoid repeating
  `access_id`/`access_key` on every task with `module_defaults`.
- **[Skip per-task auth](token-caching.md)**: wire the cache plugin so
  large playbooks don't pay the auth round-trip on every task.
- **[Bootstrap a host](bootstrap-host.md)**: fan multiple secrets into
  `host_vars` via the `akeyless_bootstrap` role.
