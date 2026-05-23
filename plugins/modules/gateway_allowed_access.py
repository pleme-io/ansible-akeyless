#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_allowed_access
short_description: Manages gateway allowed access in Akeyless
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_allowed_access resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    SubClaimsCaseInsensitive:
      description: ""
      type: bool
    access_id:
      description: "The access ID to attach to this allowed access"
      type: str
      required: true
    case_sensitive:
      description: "Treat sub claims as case-sensitive [true/false]"
      type: str
    description:
      description: "Allowed access description"
      type: str
    name:
      description: "Allowed access name"
      type: str
      required: true
    permissions:
      description: "Comma-separated list of permissions: defaults, targets, classic_keys, automatic_migration, ldap_auth, dynamic_secret, k8s_auth, log_forwarding, zero_knowledge_encryption, rotated_secret, caching, event_forwarding, admin, kmip, general, rotate_secret_value"
      type: str
    sub_claims:
      description: "Key/val of sub claims, e.g. group=admins,developers"
      type: dict
'''

EXAMPLES = r'''
- name: Create gateway_allowed_access
  gateway_allowed_access:
    state: present

- name: Delete gateway_allowed_access
  gateway_allowed_access:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

argument_spec = {
    'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
    'SubClaimsCaseInsensitive': {'type': 'bool'},
    'access_id': {'type': 'str', 'required': True},
    'case_sensitive': {'type': 'str'},
    'description': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'permissions': {'type': 'str'},
    'sub_claims': {'type': 'dict'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_allowed_access",
        sdk_create=("GatewayCreateAllowedAccess", "gateway_create_allowed_access"),
        sdk_update=("GatewayUpdateAllowedAccess", "gateway_update_allowed_access"),
        sdk_delete=("GatewayDeleteAllowedAccess", "gateway_delete_allowed_access"),
        sdk_read=("GatewayGetAllowedAccess", "gateway_get_allowed_access"),
    )


if __name__ == '__main__':
    main()
