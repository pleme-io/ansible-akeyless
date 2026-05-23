# Install a TLS certificate — the `akeyless_install_certificate` role

The `akeyless_install_certificate` role materialises a cert + key pair
from Akeyless onto a target host's filesystem, with the right
permissions, and optionally triggers a service reload.

## When to use it

- You're issuing certificates from an Akeyless PKI issuer and need
  them on disk (nginx, haproxy, postfix, etc).
- You're storing pre-issued certificates as static secrets and want
  to deploy them.
- You want atomic write semantics (no half-written certs) + the
  trigger-reload-when-changed handler pattern.

## Minimum playbook

```yaml
- hosts: nginx
  roles:
    - role: drzln0.akeyless.akeyless_install_certificate
      vars:
        akeyless_install_certificate_cert_secret: /pki/web/cert
        akeyless_install_certificate_key_secret: /pki/web/key
        akeyless_install_certificate_cert_path: /etc/nginx/ssl/web.crt
        akeyless_install_certificate_key_path:  /etc/nginx/ssl/web.key
        akeyless_install_certificate_notify: "reload nginx"

  handlers:
    - name: reload nginx
      ansible.builtin.systemd:
        name: nginx
        state: reloaded
```

What happens:
1. The role fetches the cert + key from Akeyless (via the `secret`
   lookup; supports static OR `b64decode_secret`-wrapped values).
2. Writes the cert at `0644` and the key at `0600`.
3. Both files use atomic-rename semantics — no half-written content
   visible to nginx.
4. Notifies the `reload nginx` handler IF either file changed.

## Owner / group / mode customisation

```yaml
- role: drzln0.akeyless.akeyless_install_certificate
  vars:
    akeyless_install_certificate_cert_path: /etc/postfix/ssl/server.pem
    akeyless_install_certificate_key_path: /etc/postfix/ssl/server.key
    akeyless_install_certificate_cert_secret: /pki/postfix/cert
    akeyless_install_certificate_key_secret: /pki/postfix/key
    akeyless_install_certificate_cert_owner: postfix
    akeyless_install_certificate_cert_group: postfix
    akeyless_install_certificate_cert_mode: '0644'
    akeyless_install_certificate_key_owner: postfix
    akeyless_install_certificate_key_group: postfix
    akeyless_install_certificate_key_mode: '0600'
```

## Issuing a fresh cert from a PKI issuer

When the source is a PKI issuer (not a stored secret), the role
combines with the `pki_certificate` lookup. Two-step pattern:

```yaml
- hosts: nginx
  tasks:
    - name: Issue a fresh server cert
      ansible.builtin.set_fact:
        web_cert: "{{ lookup('drzln0.akeyless.pki_certificate',
                              '/pki/server-issuer',
                              common_name=inventory_hostname,
                              alt_names=ansible_fqdn) }}"

    - name: Install the issued cert via copy
      ansible.builtin.copy:
        content: "{{ web_cert.cert }}"
        dest: /etc/nginx/ssl/server.crt
        mode: '0644'
      notify: reload nginx

    - name: Install the issued private key
      ansible.builtin.copy:
        content: "{{ web_cert.private_key }}"
        dest: /etc/nginx/ssl/server.key
        mode: '0600'
      notify: reload nginx
```

For most use cases the role is enough; drop to the manual pattern
above only when you need per-cert variation beyond what the role's
vars cover.

## Split a CA bundle

If you're installing a CA bundle (multiple certs concatenated), use
the `split_pem_bundle` filter to drop one cert per file:

```yaml
- name: Install each trust root separately
  ansible.builtin.copy:
    content: "{{ item.0 }}"
    dest: "/etc/ssl/certs/akeyless-{{ item.1 }}.pem"
    mode: '0644'
  loop: "{{ lookup('drzln0.akeyless.secret', '/ca/bundle')
            | drzln0.akeyless.split_pem_bundle
            | zip(range(100)) | list }}"
```
