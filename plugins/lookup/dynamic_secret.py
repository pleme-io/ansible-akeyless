# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: dynamic_secret
author:
  - "pleme-io (@pleme-io)"
short_description: Retrieve dynamic secret values from Akeyless Vault
version_added: "0.2.5"
description:
  - Fetches one or more dynamic secret values from Akeyless using the V2 API.
  - Dynamic secrets are ephemeral credentials minted on demand (e.g. DB
    creds, AWS STS tokens). Each call typically issues NEW credentials
    with a TTL set on the upstream dynamic-secret config.
  - "Returns a list of result dicts (one per term, in order). The exact
    shape depends on the producer type (db, aws, custom, ...) -- see
    the producer's Akeyless docs."

options:
  _terms:
    description: Dynamic secret name(s) / path(s) to retrieve.
    required: true
    type: list
    elements: str
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
    description: Auth method type (access_key, api_key, aws_iam, etc.).
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
- name: Mint dynamic DB credentials
  ansible.builtin.set_fact:
    db_creds: "{{ lookup('drzln0.akeyless.dynamic_secret',
                  '/db/postgres/readonly') }}"

- name: Use the issued credentials
  community.postgresql.postgresql_query:
    login_user: "{{ db_creds.user }}"
    login_password: "{{ db_creds.password }}"
    query: "SELECT 1"
"""

RETURN = """
_raw:
  description: One dict per term (in order); shape depends on the
               producer type. Most carry user/password/ttl fields.
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
)

try:
    import akeyless
except ImportError:  # pragma: no cover - HAS_AKEYLESS handles this
    pass


@akeyless_lookup()
class LookupModule(LookupBase):
    """Mint dynamic secret values from Akeyless Vault."""

    def fetch(self, client, token, opts, term):
        # Dynamic-secret endpoints are per-secret (unlike static
        # get_secret_value which batches). Loop is handled by the
        # @akeyless_lookup decorator.
        body = akeyless.GetDynamicSecretValue(name=term, token=token)
        return client.get_dynamic_secret_value(body)
