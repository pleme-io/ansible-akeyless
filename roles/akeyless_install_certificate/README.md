# `drzln0.akeyless.akeyless_install_certificate`

Fetches a PEM certificate (and optional private key) from an Akeyless
static secret and installs it on the target host with secure perms.
Validates the fetched value via the `is_pem_block` test before
writing — no half-installed garbage.

## Why use it

Common pattern for cert-rotation playbooks: fetch the latest cert
from Akeyless, drop it where the consuming service expects, notify a
handler to restart. This role wraps that into a single role-include
with secure-by-default file permissions and per-host overrides.

## Variables

| Var | Default | What |
|---|---|---|
| `akeyless_install_certificate_cert_secret` | `""` (**required**) | Akeyless secret path containing the PEM cert. |
| `akeyless_install_certificate_key_secret` | `""` (optional) | Akeyless secret path containing the matching private key. When unset, only the cert is installed. |
| `akeyless_install_certificate_cert_path` | `/etc/ssl/certs/akeyless-cert.pem` | Target file path for the cert. |
| `akeyless_install_certificate_key_path` | `/etc/ssl/private/akeyless-cert.key` | Target file path for the key. |
| `akeyless_install_certificate_cert_owner` / `_group` / `_mode` | `root` / `root` / `0644` | Cert file ownership + mode. |
| `akeyless_install_certificate_key_owner` / `_group` / `_mode` | `root` / `root` / `0600` | Key file ownership + mode. |
| `akeyless_install_certificate_notify` | `""` | Handler name to notify when cert/key changes (e.g. `"restart nginx"`). |
| `akeyless_install_certificate_*` (auth) | `$AKEYLESS_*` env-fallback | Standard auth shim. |
| `akeyless_install_certificate_no_log` | `true` | Redact cert/key values from playbook output. |

## Usage

```yaml
- hosts: nginx
  roles:
    - role: drzln0.akeyless.akeyless_install_certificate
      vars:
        akeyless_install_certificate_cert_secret: /pki/web/cert
        akeyless_install_certificate_key_secret:  /pki/web/key
        akeyless_install_certificate_cert_path: /etc/nginx/ssl/web.crt
        akeyless_install_certificate_key_path:  /etc/nginx/ssl/web.key
        akeyless_install_certificate_notify:    "reload nginx"
```

## Tags

`akeyless,certificate` — skip via `--skip-tags akeyless` in dev runs
that don't need real creds.

## License

GPL-3.0-or-later.
