#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_snowflake
short_description: Manages a Snowflake dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_snowflake resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present

    account:
      description: "Account name"
      type: str
      required: true
    account_password:
      description: "Database Password"
      type: str

    account_username:
      description: "Database Username"
      type: str
      required: true
    auth_mode:
      description: "The authentication mode for the temporary user [password/key]"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str

    db_name:
      description: "Database name"
      type: str
      required: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key_algo:
      description: ""
      type: str
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str

    private_key:
      description: "RSA Private key (base64 encoded)"
      type: str
      required: true
    private_key_passphrase:
      description: "The Private key passphrase"
      type: str
    role:
      description: "User role"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
    warehouse:
      description: "Warehouse name"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_snowflake
  dynamic_secret_snowflake:
    state: present

- name: Delete dynamic_secret_snowflake
  dynamic_secret_snowflake:
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
    'account': {'type': 'str', 'required': True},
    'account_password': {'type': 'str', 'no_log': True},
    'account_username': {'type': 'str', 'required': True},
    'auth_mode': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'db_name': {'type': 'str', 'required': True},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'key_algo': {'type': 'str', 'no_log': False},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'private_key': {'type': 'str', 'required': True, 'no_log': True},
    'private_key_passphrase': {'type': 'str', 'no_log': True},
    'role': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'warehouse': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='dynamic_secret_snowflake',
        sdk_create=('DynamicSecretCreateSnowflake', 'dynamic_secret_create_snowflake'),
        sdk_update=('DynamicSecretUpdateSnowflake', 'dynamic_secret_update_snowflake'),
        sdk_delete=('DynamicSecretDelete', 'dynamic_secret_delete'),
        sdk_read=('DynamicSecretGet', 'dynamic_secret_get'),
    )


if __name__ == '__main__':
    main()
