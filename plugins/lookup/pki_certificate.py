# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: pki_certificate
author:
  - "pleme-io (@pleme-io)"
short_description: Issue a PKI certificate from an Akeyless PKI cert issuer
version_added: "0.2.5"
description:
  - Calls the Akeyless C(get-pki-certificate) endpoint to issue a fresh
    certificate from a configured PKI issuer (root CA / intermediate
    CA / etc).
  - Returns the resulting C({cert, private_key, ca_chain, ...}) dict
    so callers can write each component to its destination file.
  - Distinct from the C(secret) lookup (which fetches existing static
    secret values) and the C(dynamic_secret) lookup (which mints
    ephemeral arbitrary credentials).

options:
  _terms:
    description: PKI cert issuer names. Each term issues one cert.
    required: true
    type: list
    elements: str
  common_name:
    description: CN to embed in the issued cert. Required when the
                 PKI issuer template doesn't pin a default CN.
    type: str
  alt_names:
    description: Comma-separated SAN list.
    type: str
  ttl:
    description: TTL for the issued cert in seconds. Falls back to the
                 issuer's configured default when unset.
    type: int
  key_data_base64:
    description: Optional CSR (base64-encoded) to issue against instead
                 of letting Akeyless generate the key pair.
    type: str
  gateway_url:
    description: Akeyless gateway URL.
    type: str
    default: https://api.akeyless.io
    env: [{name: AKEYLESS_GATEWAY_URL}]
    vars: [{name: akeyless_gateway_url}]
  access_id:
    description: Akeyless access ID.
    type: str
    env: [{name: AKEYLESS_ACCESS_ID}]
    vars: [{name: akeyless_access_id}]
  access_key:
    description: Akeyless access key.
    type: str
    env: [{name: AKEYLESS_ACCESS_KEY}]
    vars: [{name: akeyless_access_key}]
  access_type:
    description: Auth method type.
    type: str
    default: access_key
    env: [{name: AKEYLESS_ACCESS_TYPE}]
    vars: [{name: akeyless_access_type}]
  token:
    description: Pre-issued Akeyless token. If set, skips the auth call.
    type: str
    env: [{name: AKEYLESS_TOKEN}]

requirements:
  - akeyless >= 5.0.22
"""

EXAMPLES = """
- name: Issue a server cert for nginx
  ansible.builtin.set_fact:
    nginx_cert: "{{ lookup('drzln0.akeyless.pki_certificate',
                    '/pki/server-issuer',
                    common_name='nginx.svc.cluster.local',
                    alt_names='nginx,nginx-svc') }}"

- name: Write the cert + key
  ansible.builtin.copy:
    content: "{{ nginx_cert.cert }}"
    dest: /etc/nginx/ssl/server.crt
    mode: '0644'
"""

RETURN = """
_raw:
  description: One dict per term (in order); shape mirrors Akeyless's
               get-pki-certificate response: cert (PEM), private_key
               (PEM, when issuer-side-generated), ca_chain (list of
               PEM), parent_cert (PEM), etc.
  type: list
  elements: dict
"""

from ansible.plugins.lookup import LookupBase
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth import (
    HAS_AKEYLESS,
    AKEYLESS_IMPORT_ERROR,
)
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_plugin_helpers import (
    akeyless_lookup,
    compact_kwargs,
)

try:
    import akeyless
except ImportError:  # pragma: no cover - HAS_AKEYLESS handles this
    pass


_CERT_EXTRA_OPTS = ("common_name", "alt_names", "ttl", "key_data_base64")


@akeyless_lookup(extra_opts=_CERT_EXTRA_OPTS)
class LookupModule(LookupBase):
    """Issue PKI certificates from Akeyless cert issuers."""

    def fetch(self, client, token, opts, term):
        body = akeyless.GetPKICertificate(
            cert_issuer_name=term,
            token=token,
            **compact_kwargs(opts, _CERT_EXTRA_OPTS),
        )
        return client.get_pki_certificate(body)
