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

from typing import Any, Dict, List, Optional, Tuple

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.plugins.lookup import LookupBase

try:
    import akeyless
    from akeyless.exceptions import ApiException
    HAS_AKEYLESS = True
    AKEYLESS_IMPORT_ERROR: Optional[ImportError] = None
except ImportError as exc:
    HAS_AKEYLESS = False
    AKEYLESS_IMPORT_ERROR = exc

DEFAULT_GATEWAY_URL = "https://api.akeyless.io"
DEFAULT_ACCESS_TYPE = "access_key"


def _authenticated_client(opts: Dict[str, Any]) -> Tuple[Any, str]:
    if not HAS_AKEYLESS:
        raise AnsibleError(
            "The 'akeyless' Python package is required. "
            "Install with: pip install 'akeyless>=5.0.22'. "
            f"Original error: {AKEYLESS_IMPORT_ERROR}"
        )

    gateway_url = opts.get("gateway_url") or DEFAULT_GATEWAY_URL
    config = akeyless.Configuration(host=gateway_url)
    client = akeyless.V2Api(akeyless.ApiClient(config))

    pre_issued = opts.get("token")
    if pre_issued:
        return client, pre_issued

    access_id = opts.get("access_id")
    if not access_id:
        raise AnsibleError(
            "access_id is required when no pre-issued token is provided"
        )

    auth_body = akeyless.Auth(
        access_id=access_id,
        access_key=opts.get("access_key"),
        access_type=opts.get("access_type") or DEFAULT_ACCESS_TYPE,
    )
    try:
        auth_res = client.auth(auth_body)
    except ApiException as exc:
        status = getattr(exc, "status", "?")
        raise AnsibleError(
            f"Akeyless auth failed ({status}): {exc.body or exc.reason}"
        ) from exc

    token = getattr(auth_res, "token", None)
    if not token:
        raise AnsibleError("Akeyless auth succeeded but returned no token")
    return client, token


class LookupModule(LookupBase):
    """Issue PKI certificates from Akeyless cert issuers."""

    def run(self, terms: List[str], variables: Optional[Dict[str, Any]] = None,
            **kwargs: Any) -> List[Any]:
        self.set_options(var_options=variables, direct=kwargs)
        opts = {k: self.get_option(k) for k in (
            "gateway_url", "access_id", "access_key", "access_type", "token",
            "common_name", "alt_names", "ttl", "key_data_base64",
        )}

        client, token = _authenticated_client(opts)

        # Build the cert-issue body. Akeyless's GetPKICertificate
        # accepts the issuer name + optional CN/SAN/TTL/CSR overrides.
        cert_kwargs = {
            "token": token,
        }
        for k in ("common_name", "alt_names", "ttl", "key_data_base64"):
            v = opts.get(k)
            if v is not None and v != "":
                cert_kwargs[k] = v

        out: List[Any] = []
        for term in terms:
            body = akeyless.GetPKICertificate(cert_issuer_name=term, **cert_kwargs)
            try:
                result = client.get_pki_certificate(body)
            except ApiException as exc:
                status = getattr(exc, "status", "?")
                raise AnsibleLookupError(
                    f"Akeyless get_pki_certificate({term!r}) failed "
                    f"({status}): {exc.body or exc.reason}"
                ) from exc
            if hasattr(result, "to_dict"):
                result = result.to_dict()
            out.append(result)
        return out
