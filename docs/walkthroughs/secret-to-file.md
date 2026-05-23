# Atomic secret-to-file — the `secret_to_file` action plugin

`drzln0.akeyless.secret_to_file` fetches a secret on the Ansible
controller and atomically writes it to a path on the target host —
without the secret value ever appearing in task-arg rendering or
verbose logs.

## Why an action plugin (not a module)

The standard pattern of
`ansible.builtin.copy: { content: "{{ lookup('drzln0.akeyless.secret', '/x') }}" }`
works, but the resolved secret value passes through Ansible's
task-arg rendering layer. Aggressive `-v` output OR a downstream
callback that introspects args can log the secret.

Action plugins run on the controller side; they can fetch the secret,
hand it to the target's `copy` module via the secure transfer
mechanism, and never echo the value through arg rendering.

## Minimum task

```yaml
- name: Materialise the API token onto disk
  drzln0.akeyless.secret_to_file:
    secret: /platform/prod/api/token
    dest: /etc/app/api-token
    owner: app
    group: app
    mode: '0600'
```

Behind the scenes the action plugin:
1. Validates the args (`secret` + `dest` required; others rejected
   loudly).
2. Fetches the secret via the `secret` lookup (so auth options
   flow through normally).
3. Calls `ansible.builtin.copy` on the target with the resolved
   value, the requested perms, and a redacted `invocation.module_args`
   so the value never appears in the result.

## All accepted args

| Arg | Required | Description |
|---|---|---|
| `secret` | yes | Akeyless secret path |
| `dest` | yes | Target file path |
| `owner`, `group`, `mode` | no | Forwarded to `ansible.builtin.copy` |
| `backup` | no | Forwarded; if true, copy keeps a backup on change |
| `force` | no | Forwarded; if false, copy is no-op when dest exists |
| `gateway_url`, `access_id`, `access_key`, `access_type`, `token` | no | Auth options (or set via env vars / `module_defaults`) |

Any other arg name raises `AnsibleActionFail` immediately — catches
typos like `owener` or `accesss_key` that would silently no-op
otherwise.

## With `no_log` + redaction belt-and-suspenders

The action plugin already strips the secret value from
`invocation.module_args.content`. Add `no_log: true` on the task
for an additional layer:

```yaml
- drzln0.akeyless.secret_to_file:
    secret: /pki/web/server-cert
    dest: /etc/nginx/ssl/server.crt
    mode: '0644'
  no_log: true
```

## Composing with `module_defaults`

When you set `module_defaults: group/drzln0.akeyless.all:` (see
[Auth once per play](module-defaults.md)), `secret_to_file` inherits
the auth options just like every other module.

```yaml
- hosts: web
  module_defaults:
    group/drzln0.akeyless.all:
      access_id: "{{ akeyless_access_id }}"
      access_key: "{{ akeyless_access_key }}"

  tasks:
    - drzln0.akeyless.secret_to_file:
        secret: /platform/prod/api/token
        dest: /etc/app/api-token
        mode: '0600'
        # auth options come from the group default
```

## When to use this vs. the role

- Use `secret_to_file` for ONE file per task. It's the lowest-
  overhead atomic-write pattern.
- Use `akeyless_install_certificate` when you need cert + key
  together with the standard nginx-style reload handler.
- Use `akeyless_bootstrap` when you need MANY secrets pulled into
  one host fact for downstream tasks to reference.
