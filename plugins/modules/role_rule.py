#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role_rule
short_description: Manages a role rule in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage role_rule resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    capability:
      description: "Permission capability: read, create, update, delete, list, deny"
      type: list
      required: true
      elements: str
    path:
      description: "Item path the rule applies to"
      type: str
      required: true
    role_name:
      description: "Role name to attach the rule to"
      type: str
      required: true
    rule_type:
      description: "Rule type: item-rule or auth-method-rule or role-rule"
      type: str
    ttl:
      description: "RoleRule ttl"
      type: int
'''

EXAMPLES = r'''
- name: Create role_rule
  role_rule:
    state: present

- name: Delete role_rule
  role_rule:
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
    'capability': {'type': 'list', 'required': True, 'elements': 'str'},
    'path': {'type': 'str', 'required': True},
    'role_name': {'type': 'str', 'required': True},
    'rule_type': {'type': 'str'},
    'ttl': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="role_rule",
        sdk_create=("SetRoleRule", "set_role_rule"),
        # WARNING: The following fields are immutable after creation.
        #   - capability
        #   - path
        #   - role_name
        # Changing them requires destroy + recreate.
        sdk_update=None,
        immutable=True,
        sdk_delete=("DeleteRoleRule", "delete_role_rule"),
        sdk_read=("GetRole", "get_role"),
        read_key="role_name",
    )


if __name__ == '__main__':
    main()
