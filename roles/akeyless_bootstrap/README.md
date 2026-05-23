# `drzln0.akeyless.akeyless_bootstrap`

Bootstraps Akeyless authentication for a play and exposes a configurable
set of static secrets as a host-scoped fact, so subsequent tasks can
reference them without repeating lookup boilerplate.

## Why use it

The `drzln0.akeyless.secret` lookup is the right tool for individual
secret reads, but tracks like *"every task in this play needs the same
five secrets"* end up with the same lookup-call boilerplate spread
across every task. This role centralises the fetch into one call and
keeps the rest of the play noise-free.

## Variables

| Var | Default | What |
|---|---|---|
| `akeyless_bootstrap_secrets` | `[]` (**required**) | List of secret paths to fetch. |
| `akeyless_bootstrap_var_name` | `akeyless_secrets` | Host-scoped fact name where resolved secrets land. Keys are the basename of each path. |
| `akeyless_bootstrap_gateway_url` | `$AKEYLESS_GATEWAY_URL` or `https://api.akeyless.io` | Gateway endpoint. |
| `akeyless_bootstrap_access_id` | `$AKEYLESS_ACCESS_ID` | Auth ID. |
| `akeyless_bootstrap_access_key` | `$AKEYLESS_ACCESS_KEY` | Auth secret. |
| `akeyless_bootstrap_access_type` | `$AKEYLESS_ACCESS_TYPE` or `access_key` | Auth method. |
| `akeyless_bootstrap_token` | `$AKEYLESS_TOKEN` | Pre-issued token (skips auth). |
| `akeyless_bootstrap_no_log` | `true` | When true, the set_fact tasks redact resolved values from logs. |

## Usage

```yaml
- hosts: all
  roles:
    - role: drzln0.akeyless.akeyless_bootstrap
      vars:
        akeyless_bootstrap_secrets:
          - /platform/prod/db/password
          - /platform/prod/api/jwt-key
          - /platform/prod/smtp/credentials

  tasks:
    # akeyless_secrets is now {password: ..., jwt-key: ..., credentials: ...}
    - name: Render config file
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/app/app.conf
      vars:
        db_pass: "{{ akeyless_secrets['password'] }}"
        jwt_key: "{{ akeyless_secrets['jwt-key'] }}"
```

## Tags

Tasks are tagged `akeyless,bootstrap` so you can `--skip-tags akeyless`
in dev runs that don't need real creds.

## License

GPL-3.0-or-later (matches the rest of `drzln0.akeyless`).
