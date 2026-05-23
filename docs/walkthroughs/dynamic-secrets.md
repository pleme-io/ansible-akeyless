# Dynamic + rotated secrets

Akeyless has three categories of secret. This collection wraps all
three; this walkthrough covers the two ephemeral ones.

| Category | Lifetime | Use case |
|---|---|---|
| **Static** | Long-lived | API keys, passwords you control rotation for |
| **Rotated** | Long-lived but auto-rotated | DB users where Akeyless owns rotation |
| **Dynamic** | Ephemeral (minted per-call) | Just-in-time DB creds, AWS STS tokens |

## Dynamic secrets — mint ephemeral credentials per call

Each call to the `dynamic_secret` lookup mints NEW credentials with
a TTL set on the producer config. After the TTL, the credentials
self-revoke server-side.

```yaml
- name: Mint DB credentials valid for 30 minutes
  ansible.builtin.set_fact:
    db_creds: "{{ lookup('drzln0.akeyless.dynamic_secret',
                  '/dynamic/db/postgres-readonly') }}"
  no_log: true

- name: Use the ephemeral creds
  community.postgresql.postgresql_query:
    login_user: "{{ db_creds.user }}"
    login_password: "{{ db_creds.password }}"
    query: "SELECT * FROM events WHERE created_at > now() - interval '1 hour'"
  no_log: true
```

The shape of `db_creds` depends on the upstream producer type
(postgres, mysql, aws, custom, ...). For DB producers it typically
includes `user`, `password`, `ttl`, and `id` (the lease ID; pass it
to `dynamic_secret_revoke_creds` for early revocation).

### Producing the dynamic-secret config

The producer itself is configured via the
`dynamic_secret_postgresql` module (one per DB type):

```yaml
- drzln0.akeyless.dynamic_secret_postgresql:
    name: /dynamic/db/postgres-readonly
    target_name: /targets/prod-db
    user_ttl: 30m
    postgresql_db_name: appdb
    postgresql_statements: |
      CREATE USER "{{name}}" WITH PASSWORD '{{password}}';
      GRANT pg_read_all_data TO "{{name}}";
    state: present
```

`{{name}}` and `{{password}}` here are Akeyless template
placeholders, not Ansible templating — Akeyless substitutes them
when minting each new credential.

## Rotated secrets — long-lived but auto-rotated

Rotated secrets sit between static and dynamic: there's ONE
credential at any time, but Akeyless auto-rotates it on the
schedule you set. Consumers always read the current value via the
`secret` lookup.

```yaml
- drzln0.akeyless.rotated_secret_postgresql:
    name: /rotated/db/app-readwrite
    target_name: /targets/prod-db
    rotation_hour: 2          # 02:00
    rotation_interval: 30     # days
    authentication_credentials: use-user-creds
    rotated_username: app_rw
    rotated_password: "{{ initial_password }}"
    state: present
```

Then consumers read the CURRENT value with the standard `secret`
lookup:

```yaml
- name: Connect with the current rotated password
  community.postgresql.postgresql_query:
    login_user: app_rw
    login_password: "{{ lookup('drzln0.akeyless.secret',
                                '/rotated/db/app-readwrite') }}"
  no_log: true
```

## Pick the right shape

- **Static** — you control rotation (legacy API keys, third-party
  tokens that don't expose a rotation API).
- **Rotated** — Akeyless can rotate it AND consumers can tolerate a
  reconnect when rotation happens. DB users, service accounts.
- **Dynamic** — every call should get a NEW credential. Short-lived
  jobs, CI/CD, exploratory scripts. Minimum-blast-radius posture.

## Combining with the cache plugin

The [`akeyless_token` cache plugin](token-caching.md) caches your
auth token, not the secret values. Dynamic + rotated secret lookups
still hit the gateway each call (that's the whole point of
ephemeral creds). The cache just removes the re-auth overhead.
