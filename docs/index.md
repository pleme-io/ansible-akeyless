# `drzln0.akeyless` — Documentation

Auto-generated Ansible Collection wrapping the entire Akeyless V2 API,
plus hand-tuned lookup / inventory / filter / test / callback / action /
cache plugins and ready-to-use roles.

## Quick install

```bash
ansible-galaxy collection install drzln0.akeyless
```

## What ships

- **209 modules** covering every resource the Akeyless V2 API exposes
  (auth methods, roles, static / dynamic / rotated secrets, targets,
  keys, gateway producers, log forwarding, KMIP, certificate
  lifecycle).
- **3 lookup plugins** for fetching secret values in Jinja2:
  `secret`, `dynamic_secret`, `pki_certificate`.
- **1 inventory plugin** for treating Akeyless JSON-shaped secrets as
  the inventory source.
- **7 filter plugins** for transforming secret payloads:
  `b64decode_secret`, `parse_dotenv_secret`, `secret_to_json`,
  `split_pem_bundle`, `secret_keys_to_env`, `mask_secret`,
  `secret_strength`.
- **4 test plugins** for validation: `is_akeyless_path`,
  `is_akeyless_access_id`, `is_pem_block`, `is_base64`.
- **1 callback plugin** for defensive secret redaction on stdout
  (`akeyless_redactor`).
- **1 action plugin** for atomic secret-to-file materialisation
  (`secret_to_file`).
- **1 cache plugin** for cross-task token reuse (`akeyless_token`).
- **2 roles**: `akeyless_bootstrap`, `akeyless_install_certificate`.
- **2 example playbooks**.

## Walkthroughs

The fastest path from "I just installed this" to "production playbook":

| Walkthrough | What you build |
|---|---|
| [Quickstart](walkthroughs/quickstart.md) | First secret fetch via the `secret` lookup |
| [Auth once via action_groups](walkthroughs/module-defaults.md) | Set Akeyless auth on every task in a play with one block |
| [Bootstrap a host with secrets](walkthroughs/bootstrap-host.md) | Use the `akeyless_bootstrap` role to fan secrets out to hostvars |
| [Install a TLS certificate](walkthroughs/install-tls-cert.md) | Materialise a cert + key pair from Akeyless onto a target |
| [Inventory from Akeyless](walkthroughs/inventory-from-akeyless.md) | Treat Akeyless JSON secrets as your AWX/AAP inventory source |
| [Atomic secret-to-file](walkthroughs/secret-to-file.md) | Drop a secret onto disk without it ever appearing in task args |
| [Skip per-task auth](walkthroughs/token-caching.md) | Wire the cache plugin so auth runs ONCE per playbook |
| [Dynamic + rotated secrets](walkthroughs/dynamic-secrets.md) | Mint ephemeral DB creds + rotation policies |
| [AWX / AAP integration](walkthroughs/awx-aap-integration.md) | Run this collection inside Tower with credential delegation |

## Reference

- [Architecture](reference/architecture.md) — how the helper, decorators,
  and per-plugin layout fit together.
- [Authentication options](reference/authentication.md) — all auth
  methods, env vars, and precedence rules.
- [Per-module docs](https://github.com/pleme-io/ansible-akeyless/tree/main/plugins/modules)
  — generated from each module's DOCUMENTATION block; render with
  `ansible-doc drzln0.akeyless.<module>`.

## Project links

- [Source on GitHub](https://github.com/pleme-io/ansible-akeyless)
- [Galaxy collection page](https://galaxy.ansible.com/drzln0/akeyless)
- [Changelog](https://github.com/pleme-io/ansible-akeyless/blob/main/CHANGELOG.md)
- [Issue tracker](https://github.com/pleme-io/ansible-akeyless/issues)
