# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: secret
author:
  - "pleme-io (@pleme-io)"
short_description: Retrieve static secret values from Akeyless Vault
version_added: "0.2.0"
description:
  - Fetches one or more static secret values from Akeyless using the V2 API.
  - Returns the values in the same order as the terms.
  - Authenticates per-lookup using the access-key auth flow by default.

options:
  _terms:
    description: Secret name(s) / path(s) to retrieve.
    required: true
    type: list
    elements: str
  gateway_url:
    description: Akeyless gateway URL.
    type: str
    default: https://api.akeyless.io
    env:
      - name: AKEYLESS_GATEWAY_URL
    vars:
      - name: akeyless_gateway_url
  access_id:
    description: Akeyless access ID.
    type: str
    env:
      - name: AKEYLESS_ACCESS_ID
    vars:
      - name: akeyless_access_id
  access_key:
    description: Akeyless access key.
    type: str
    env:
      - name: AKEYLESS_ACCESS_KEY
    vars:
      - name: akeyless_access_key
  access_type:
    description: Auth method type (access_key, api_key, aws_iam, etc.).
    type: str
    default: access_key
    env:
      - name: AKEYLESS_ACCESS_TYPE
    vars:
      - name: akeyless_access_type
  token:
    description: Pre-issued Akeyless token. If set, skips the auth call.
    type: str
    env:
      - name: AKEYLESS_TOKEN

requirements:
  - akeyless >= 5.0.22
"""

EXAMPLES = """
- name: Fetch one static secret
  ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/app/db/password') }}"

- name: Fetch multiple secrets in order
  ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/app/db/user', '/app/db/password') }}"

- name: Use a pre-issued token
  ansible.builtin.set_fact:
    api_key: "{{ lookup('drzln0.akeyless.secret', '/svc/api_key', token=tmp_token) }}"

- name: Hand auth params per-task instead of env
  ansible.builtin.debug:
    msg: "{{ lookup('drzln0.akeyless.secret', '/x', access_id=aid, access_key=ak) }}"
"""

RETURN = """
_raw:
  description: The secret value(s) — one entry per input term, in order.
  type: list
  elements: str
"""

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.plugins.lookup import LookupBase

try:
    import akeyless
    from akeyless.exceptions import ApiException
    HAS_AKEYLESS = True
    AKEYLESS_IMPORT_ERROR = None
except ImportError as exc:
    HAS_AKEYLESS = False
    AKEYLESS_IMPORT_ERROR = exc


def _authenticated_client(opts):
    """Build a V2Api client + token from lookup options."""
    if not HAS_AKEYLESS:
        raise AnsibleError(
            "The 'akeyless' Python package is required. "
            "Install with: pip install 'akeyless>=5.0.22'. "
            "Original error: %s" % AKEYLESS_IMPORT_ERROR
        )

    gateway_url = opts.get('gateway_url') or 'https://api.akeyless.io'
    config = akeyless.Configuration(host=gateway_url)
    client = akeyless.V2Api(akeyless.ApiClient(config))

    pre_issued = opts.get('token')
    if pre_issued:
        return client, pre_issued

    access_id = opts.get('access_id')
    if not access_id:
        raise AnsibleError(
            "access_id is required when no pre-issued token is provided "
            "(set the access_id option, AKEYLESS_ACCESS_ID env var, or pass token=...)"
        )

    auth_body = akeyless.Auth(
        access_id=access_id,
        access_key=opts.get('access_key'),
        access_type=opts.get('access_type') or 'access_key',
    )
    try:
        auth_res = client.auth(auth_body)
    except ApiException as exc:
        raise AnsibleError(
            "Akeyless auth failed (%s): %s" % (
                getattr(exc, 'status', '?'),
                exc.body or exc.reason,
            )
        )

    token = getattr(auth_res, 'token', None)
    if not token:
        raise AnsibleError("Akeyless auth succeeded but returned no token")
    return client, token


class LookupModule(LookupBase):
    """Fetch static secret values from Akeyless Vault."""

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        opts = {k: self.get_option(k) for k in (
            'gateway_url', 'access_id', 'access_key', 'access_type', 'token',
        )}

        client, token = _authenticated_client(opts)

        # Akeyless /get-secret-value accepts a list of names and returns
        # a {name: value} mapping. We send all terms in one call for
        # efficiency, then reorder the result to match the input.
        body = akeyless.GetSecretValue(names=list(terms), token=token)
        try:
            result = client.get_secret_value(body)
        except ApiException as exc:
            raise AnsibleLookupError(
                "Akeyless get_secret_value failed (%s): %s" % (
                    getattr(exc, 'status', '?'),
                    exc.body or exc.reason,
                )
            )

        # The SDK returns a model with `.to_dict()` or a plain dict
        # depending on version; normalise.
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        if not isinstance(result, dict):
            raise AnsibleLookupError(
                "Unexpected get_secret_value response type: %s" % type(result).__name__
            )

        out = []
        for term in terms:
            if term not in result:
                raise AnsibleLookupError(
                    "Secret %r not found in Akeyless response" % term
                )
            out.append(result[term])
        return out
