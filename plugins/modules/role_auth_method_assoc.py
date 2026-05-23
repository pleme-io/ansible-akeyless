#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role_auth_method_assoc
short_description: Manages a role-to-auth-method association in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage role_auth_method_assoc resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    am_name:
      description: "Auth method name to associate with the role"
      type: str
      required: true
    case_sensitive:
      description: "Case-sensitive sub-claims matching"
      type: str
    role_name:
      description: "Role name to associate"
      type: str
      required: true
    sub_claims:
      description: "Sub-claims for the association (key=value pairs)"
      type: dict
'''

EXAMPLES = r'''
- name: Create role_auth_method_assoc
  role_auth_method_assoc:
    state: present

- name: Delete role_auth_method_assoc
  role_auth_method_assoc:
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
    'am_name': {'type': 'str', 'required': True},
    'case_sensitive': {'type': 'str'},
    'role_name': {'type': 'str', 'required': True},
    'sub_claims': {'type': 'dict'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="role_auth_method_assoc",
        sdk_create=("AssocRoleAuthMethod", "assoc_role_auth_method"),
        # WARNING: The following fields are immutable after creation.
        #   - am_name
        # Changing them requires destroy + recreate.
        sdk_update=None,
        immutable=True,
        sdk_delete=("DeleteRoleAssociation", "delete_role_association"),
        sdk_read=("GetRole", "get_role"),
    )


if __name__ == '__main__':
    main()
