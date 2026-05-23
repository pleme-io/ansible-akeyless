# Inventory from Akeyless — the inventory plugin

The `drzln0.akeyless.akeyless` inventory plugin treats Akeyless
JSON-shaped static secrets as the source of truth for your Ansible
inventory. Hosts + groups + vars all flow from one (or more) JSON
documents stored in Akeyless.

## When to use it

- Your inventory is dynamic and you don't want to maintain a
  separate inventory file or hosted dynamic-inventory service.
- You already store inventory-like metadata in Akeyless (host lists,
  per-host vars, group memberships) and want Ansible to consume it
  natively.
- You're running playbooks inside AWX / AAP and want the inventory
  itself to come from your Akeyless tenant.

## The secret shape

The plugin parses each referenced secret as JSON with this shape:

```json
{
  "hosts": {
    "web1.prod": {
      "ansible_host": "10.0.1.10",
      "ansible_user": "ec2-user"
    },
    "web2.prod": {
      "ansible_host": "10.0.1.11",
      "ansible_user": "ec2-user"
    }
  },
  "groups": {
    "web":  {"hosts": ["web1.prod", "web2.prod"],
              "vars": {"role": "web"}},
    "prod": {"hosts": ["web1.prod", "web2.prod"]}
  }
}
```

Both top-level keys (`hosts`, `groups`) are optional. Unknown keys
are silently ignored (forward-compat for future metadata).

## Wiring it up

Inventory config file (must end in `.akeyless.yml` or `.akeyless.yaml`):

```yaml
# inventory/prod.akeyless.yml
plugin: drzln0.akeyless.akeyless
secrets:
  - /platform/prod/inventory
```

Run with:

```bash
AKEYLESS_ACCESS_ID=p-abc \
AKEYLESS_ACCESS_KEY=k-xyz \
  ansible-inventory -i inventory/prod.akeyless.yml --list
```

Or as the `-i` for any playbook:

```bash
ansible-playbook -i inventory/prod.akeyless.yml site.yml
```

## Composing multiple secrets

Pass multiple secret paths to merge them into one inventory tree:

```yaml
plugin: drzln0.akeyless.akeyless
secrets:
  - /platform/prod/inventory
  - /platform/prod/overrides
  - /platform/edge/inventory
```

Later secrets override earlier ones for the same host/group name —
useful for layering an env-wide template with per-region overrides.

## With ansible.cfg

If every inventory in your repo uses Akeyless, point ansible.cfg at
the plugin so any `*.akeyless.yml` file works as an `-i`:

```ini
# ansible.cfg
[inventory]
enable_plugins = drzln0.akeyless.akeyless, host_list, script, auto, yaml, ini
```

## AWX / AAP integration

In AWX / AAP, register `drzln0.akeyless.akeyless` as a custom
inventory source pointed at the `.akeyless.yml` file in your project.
The plugin reads its `secrets:` list from the YAML and the auth
options from environment variables you set in the inventory source's
"environment" tab.

See [AWX / AAP integration](awx-aap-integration.md) for the full
credential-delegation pattern.

## Auth options

The inventory plugin accepts the same auth options every other plugin
in this collection takes (`gateway_url`, `access_id`, `access_key`,
`access_type`, `token`). Each falls back to its `AKEYLESS_*` env var.

For inventory plugins specifically, AWX/AAP injects the env vars from
the inventory source's "credential" binding — that's the recommended
way to give the inventory plugin its credentials in a controller
environment.
