#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: account_custom_field
short_description: Manages an account custom field in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage account_custom_field resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    name:
      description: "The name of the custom field"
      type: str
      required: true
    object:
      description: "The object to create the custom field"
      type: str
      required: true
    object_type:
      description: "The object type to create the custom field [e.g. STATIC_SECRET,DYNAMIC_SECRET,ROTATED_SECRET]"
      type: str
      required: true
    required:
      description: "Specify whether the custom field is mandatory"
      type: bool
'''

EXAMPLES = r'''
- name: Create account_custom_field
  account_custom_field:
    state: present

- name: Delete account_custom_field
  account_custom_field:
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
    'name': {'type': 'str', 'required': True},
    'object': {'type': 'str', 'required': True},
    'object_type': {'type': 'str', 'required': True},
    'required': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="account_custom_field",
        sdk_create=("AccountCustomFieldCreate", "account_custom_field_create"),
        sdk_update=("AccountCustomFieldUpdate", "account_custom_field_update"),
        sdk_delete=("AccountCustomFieldDelete", "account_custom_field_delete"),
        sdk_read=("AccountCustomFieldGet", "account_custom_field_get"),
    )


if __name__ == '__main__':
    main()
