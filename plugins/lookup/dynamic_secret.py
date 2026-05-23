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

from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth import (
    DEFAULT_ACCESS_TYPE,
    DEFAULT_GATEWAY_URL,
    HAS_AKEYLESS,
    AKEYLESS_IMPORT_ERROR,
    authenticated_client as _authenticated_client,
)

try:
    import akeyless
    from akeyless.exceptions import ApiException
except ImportError:  # pragma: no cover - HAS_AKEYLESS handles this
    pass


class LookupModule(LookupBase):
    """Mint dynamic secret values from Akeyless Vault."""

    def run(self, terms: List[str], variables: Optional[Dict[str, Any]] = None,
            **kwargs: Any) -> List[Any]:
        self.set_options(var_options=variables, direct=kwargs)
        opts = {k: self.get_option(k) for k in (
            "gateway_url", "access_id", "access_key", "access_type", "token",
        )}

        client, token = _authenticated_client(opts)

        out: List[Any] = []
        # Dynamic-secret endpoints are per-secret (unlike static
        # get_secret_value which batches). Loop is intentional.
        for term in terms:
            body = akeyless.GetDynamicSecretValue(name=term, token=token)
            try:
                result = client.get_dynamic_secret_value(body)
            except ApiException as exc:
                status = getattr(exc, "status", "?")
                raise AnsibleLookupError(
                    f"Akeyless get_dynamic_secret_value({term!r}) failed "
                    f"({status}): {exc.body or exc.reason}"
                ) from exc
            if hasattr(result, "to_dict"):
                result = result.to_dict()
            out.append(result)
        return out
