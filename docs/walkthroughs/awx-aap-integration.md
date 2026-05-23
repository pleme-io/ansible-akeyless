# AWX / AAP integration

Running this collection inside AWX or Ansible Automation Platform
gets you credential delegation, scheduled runs, and the inventory
plugin all wired together.

## Install the collection in your execution environment

`requirements.yml` in your AAP project:

```yaml
collections:
  - name: drzln0.akeyless
    version: '>=0.2,<0.3'
```

`bindep.txt` (Python deps for the SDK):

```
# Akeyless SDK + Ansible runtime
akeyless [python]
ansible-core>=2.14 [python]
```

If you build your own EE with `ansible-builder`, add to your
`execution-environment.yml`:

```yaml
version: 3
dependencies:
  galaxy: requirements.yml
  python:
    - akeyless>=5.0.22
```

Then `ansible-builder build` and push to your registry.

## Credential type for Akeyless

Create a custom credential type so playbooks pick up auth env vars
without exposing the keys in the project.

**Inputs** (the form a user fills in when creating a credential):

```yaml
fields:
  - id: akeyless_access_id
    label: Akeyless Access ID
    type: string
  - id: akeyless_access_key
    label: Akeyless Access Key
    type: string
    secret: true
  - id: akeyless_gateway_url
    label: Gateway URL
    type: string
    default: https://api.akeyless.io
required:
  - akeyless_access_id
  - akeyless_access_key
```

**Injectors** (what gets exposed to the playbook env at runtime):

```yaml
env:
  AKEYLESS_ACCESS_ID:    '{{ akeyless_access_id }}'
  AKEYLESS_ACCESS_KEY:   '{{ akeyless_access_key }}'
  AKEYLESS_GATEWAY_URL:  '{{ akeyless_gateway_url }}'
```

Now any playbook that uses the `secret` lookup or any
`drzln0.akeyless.*` module reads its credentials from the AWX
credential — no hardcoded keys in git.

## Inventory source

Create an inventory source of type "Source from a project" pointing
at `inventory/prod.akeyless.yml` (the file from
[Inventory from Akeyless](inventory-from-akeyless.md)).

In the inventory source's "credential" field, attach the Akeyless
credential you just created. The injector env vars are exposed to
the inventory plugin's auth path automatically.

Set the update cadence in the inventory source's "Update Options"
panel (typically every 5-15 minutes for fast-changing inventories,
or "on launch" only if the source changes rarely).

## Cache plugin in AWX/EE

The cache plugin's directory needs to be writable inside the EE
container. Use `/runner/cache/akeyless` (writable by the `runner`
user that AWX uses) and set it in `ansible.cfg` in your project:

```ini
[defaults]
fact_caching = drzln0.akeyless.akeyless_token
fact_caching_connection = /runner/cache/akeyless
fact_caching_timeout = 1500
```

The cache is per-job (the runner container is ephemeral) but
intra-job caching still wins on multi-task plays.

## Scheduled rotation playbooks

A common AWX pattern: a scheduled job runs nightly to refresh a
batch of rotated secrets. The job uses
`drzln0.akeyless.rotated_secret_postgresql` (or similar) in idempotent
mode — Akeyless takes care of the rotation timing; the playbook just
verifies the producer config still matches the desired state.

```yaml
- hosts: localhost
  module_defaults:
    group/drzln0.akeyless.all:
      access_id: "{{ lookup('env', 'AKEYLESS_ACCESS_ID') }}"
      access_key: "{{ lookup('env', 'AKEYLESS_ACCESS_KEY') }}"

  tasks:
    - drzln0.akeyless.rotated_secret_postgresql:
        name: /rotated/db/{{ item.name }}
        target_name: "{{ item.target }}"
        rotation_hour: 2
        rotation_interval: 30
        state: present
      loop: "{{ rotation_configs }}"
```

Schedule this as an AWX job template with daily cadence.

## See also

- [Inventory from Akeyless](inventory-from-akeyless.md) — the
  inventory plugin itself.
- [Skip per-task auth](token-caching.md) — cache plugin wiring.
- [Module_defaults + action_groups](module-defaults.md) — one-block
  credential application across many tasks.
