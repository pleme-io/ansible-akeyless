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

# akeyless + ApiException re-imported locally for the get_secret_value
# dispatch + ApiException catch below. (The shared helper handles auth
# but doesn't dispatch SDK calls; that stays per-lookup so each lookup
# can shape the body / error context to its endpoint.)
try:
    import akeyless
    from akeyless.exceptions import ApiException
except ImportError:  # pragma: no cover - HAS_AKEYLESS handles this
    pass


class LookupModule(LookupBase):
    """Fetch static secret values from Akeyless Vault."""

    def run(self, terms: List[str], variables: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[Any]:
        self.set_options(var_options=variables, direct=kwargs)
        opts = {k: self.get_option(k) for k in (
            "gateway_url", "access_id", "access_key", "access_type", "token",
        )}

        client, token = _authenticated_client(opts)

        # Akeyless /get-secret-value accepts a list of names and returns
        # a {name: value} mapping. We send all terms in one call for
        # efficiency, then reorder the result to match the input.
        body = akeyless.GetSecretValue(names=list(terms), token=token)
        try:
            result = client.get_secret_value(body)
        except ApiException as exc:
            status = getattr(exc, "status", "?")
            raise AnsibleLookupError(
                f"Akeyless get_secret_value failed ({status}): "
                f"{exc.body or exc.reason}"
            ) from exc

        # The SDK returns a model with `.to_dict()` or a plain dict
        # depending on version; normalise.
        if hasattr(result, "to_dict"):
            result = result.to_dict()
        if not isinstance(result, dict):
            raise AnsibleLookupError(
                f"Unexpected get_secret_value response type: {type(result).__name__}"
            )

        out: List[Any] = []
        for term in terms:
            if term not in result:
                raise AnsibleLookupError(
                    f"Secret {term!r} not found in Akeyless response"
                )
            out.append(result[term])
        return out
