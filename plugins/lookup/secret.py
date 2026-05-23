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

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth import (
    HAS_AKEYLESS,
    AKEYLESS_IMPORT_ERROR,
)
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_plugin_helpers import (
    akeyless_lookup,
    normalize_sdk_result,
)

try:
    import akeyless
except ImportError:  # pragma: no cover - HAS_AKEYLESS handles this
    pass


@akeyless_lookup(per_term=False)
class LookupModule(LookupBase):
    """Fetch static secret values from Akeyless Vault."""

    def fetch(self, client, token, opts, terms):
        # /get-secret-value batches: send the full name list in one call,
        # then re-shape the returned {name: value} dict into a list
        # aligned to input order so terms[i] -> out[i].
        body = akeyless.GetSecretValue(names=list(terms), token=token)
        result = normalize_sdk_result(client.get_secret_value(body))
        if not isinstance(result, dict):
            raise AnsibleLookupError(
                f"Unexpected get_secret_value response type: {type(result).__name__}"
            )
        out = []
        for term in terms:
            if term not in result:
                raise AnsibleLookupError(
                    f"Secret {term!r} not found in Akeyless response"
                )
            out.append(result[term])
        return out
