#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
name: akeyless
author:
  - "pleme-io (@pleme-io)"
short_description: Inventory source backed by Akeyless Vault static secrets
description:
  - Loads inventory hosts from JSON-shaped static secrets stored in Akeyless.
  - The secret value is parsed as JSON and merged into the inventory tree.
  - "Supported JSON shape: {hosts: {name: {vars}}, groups: {name: {hosts: [...], vars: {}}}}"
  - "Addresses the Pepsico use case (PRM-1767): teams add Akeyless as an
    inventory source in AWX/AAP, then playbooks reference secrets via
    standard host_vars / group_vars without per-task lookup boilerplate."

options:
  plugin:
    description: Identifies this as the akeyless inventory plugin. Must be `drzln0.akeyless.akeyless`.
    required: true
    choices: ['drzln0.akeyless.akeyless']
  secrets:
    description: One or more Akeyless secret paths whose JSON value should be merged into the inventory.
    type: list
    elements: str
    required: true
  gateway_url:
    description: Akeyless gateway URL.
    type: str
    default: 'https://api.akeyless.io'
    env:
      - name: AKEYLESS_GATEWAY_URL
  access_id:
    description: Akeyless access ID.
    type: str
    env:
      - name: AKEYLESS_ACCESS_ID
  access_key:
    description: Akeyless access key.
    type: str
    env:
      - name: AKEYLESS_ACCESS_KEY
  access_type:
    description: Akeyless auth method.
    type: str
    default: 'access_key'
    env:
      - name: AKEYLESS_ACCESS_TYPE
  token:
    description: Pre-issued Akeyless token. Skips the auth call when set.
    type: str
    env:
      - name: AKEYLESS_TOKEN

requirements:
  - akeyless >= 5.0.22

extends_documentation_fragment:
  - constructed
'''

EXAMPLES = r'''
# Plain inventory file: inventory.akeyless.yml
plugin: drzln0.akeyless.akeyless
secrets:
  - /platform/prod/inventory
  - /platform/staging/inventory

# Stored secret JSON value example:
# {
#   "hosts": {
#     "web1.prod": {"ansible_host": "10.0.1.10", "ansible_user": "ec2-user"},
#     "web2.prod": {"ansible_host": "10.0.1.11", "ansible_user": "ec2-user"}
#   },
#   "groups": {
#     "web":  {"hosts": ["web1.prod", "web2.prod"], "vars": {"role": "web"}},
#     "prod": {"hosts": ["web1.prod", "web2.prod"]}
#   }
# }
'''

import json
from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth import (
    authenticated_client as _authenticate,
)

try:
    import akeyless
    from akeyless.exceptions import ApiException
except ImportError:  # pragma: no cover - shared helper signals SDK absence
    pass


def _fetch_secret(client: Any, token: str, name: str) -> Any:
    """Fetch a single static secret and parse its value as JSON."""
    body = akeyless.GetSecretValue(names=[name], token=token)
    try:
        result = client.get_secret_value(body)
    except ApiException as exc:
        status = getattr(exc, "status", "?")
        raise AnsibleError(
            f"Akeyless get_secret_value({name!r}) failed ({status}): "
            f"{exc.body or exc.reason}"
        ) from exc

    if hasattr(result, "to_dict"):
        result = result.to_dict()
    if not isinstance(result, dict) or name not in result:
        raise AnsibleError(
            f"Akeyless response missing secret {name!r}; got {list(result or [])}"
        )

    raw_value = result[name]
    try:
        return json.loads(raw_value)
    except (TypeError, ValueError) as exc:
        raise AnsibleError(
            f"Secret {name!r} value is not valid JSON: {exc}"
        ) from exc


def _merge_inventory_tree(
    inventory: Any,
    payload: Dict[str, Any],
    source_label: str,
) -> None:
    """Apply one parsed secret's {hosts, groups} payload to the inventory.

    payload['hosts'] is a {name: {vars}} dict; each host is added and
    its vars are set verbatim. payload['groups'] is a {name: {hosts,
    vars}} dict; each group is added with optional host membership +
    vars. Unknown top-level keys are ignored (forward-compat).
    """
    for host_name, host_vars in (payload.get("hosts") or {}).items():
        inventory.add_host(host_name)
        for k, v in (host_vars or {}).items():
            inventory.set_variable(host_name, k, v)

    for group_name, group_body in (payload.get("groups") or {}).items():
        inventory.add_group(group_name)
        for host in (group_body or {}).get("hosts") or []:
            # Auto-create the host if it wasn't declared under 'hosts'
            # earlier -- common for "group-only" inventory shapes.
            inventory.add_host(host, group=group_name)
        for k, v in ((group_body or {}).get("vars") or {}).items():
            inventory.set_variable(group_name, k, v)


class InventoryModule(BaseInventoryPlugin, Constructable):
    """Inventory plugin that loads hosts from Akeyless JSON secrets."""

    NAME = "drzln0.akeyless.akeyless"

    def verify_file(self, path: str) -> bool:
        """Allow .akeyless.yml / .akeyless.yaml suffixes (Ansible's
        convention) plus anything ending in akeyless.{yml,yaml} so
        callers can use names like inventory.akeyless.yml without the
        leading dot."""
        if not super().verify_file(path):
            return False
        return path.endswith(("akeyless.yml", "akeyless.yaml",
                              ".akeyless.yml", ".akeyless.yaml"))

    def parse(self, inventory: Any, loader: Any, path: str, cache: bool = True) -> None:
        super().parse(inventory, loader, path)
        self._read_config_data(path)

        opts = {k: self.get_option(k) for k in (
            "gateway_url", "access_id", "access_key", "access_type", "token",
        )}
        secrets: List[str] = self.get_option("secrets") or []
        if not secrets:
            raise AnsibleError(
                "akeyless inventory: `secrets` is required and must list "
                "at least one secret path"
            )

        client, token = _authenticate(opts)
        for name in secrets:
            payload = _fetch_secret(client, token, name)
            if not isinstance(payload, dict):
                raise AnsibleError(
                    f"Secret {name!r} payload must be a JSON object, got "
                    f"{type(payload).__name__}"
                )
            _merge_inventory_tree(inventory, payload, source_label=name)
