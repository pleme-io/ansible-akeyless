#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_hanadb
short_description: Manages a SAP HANA dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_hanadb resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    hana_dbname:
      description: "HanaDb Name"
      type: str
    hanadb_create_statements:
      description: "HanaDb Creation statements"
      type: str
    hanadb_host:
      description: "HANA host"
      type: str
    hanadb_password:
      description: "HANA admin password"
      type: str
      no_log: true
    hanadb_port:
      description: "HANA port (default: 443)"
      type: str
    hanadb_revocation_statements:
      description: "HANA SQL revocation statements"
      type: str
    hanadb_username:
      description: "HANA admin username"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
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
'''

EXAMPLES = r'''
- name: Create dynamic_secret_hanadb
  dynamic_secret_hanadb:
    state: present

- name: Delete dynamic_secret_hanadb
  dynamic_secret_hanadb:
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
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'hana_dbname': {'type': 'str'},
    'hanadb_create_statements': {'type': 'str'},
    'hanadb_host': {'type': 'str'},
    'hanadb_password': {'type': 'str', 'no_log': True},
    'hanadb_port': {'type': 'str'},
    'hanadb_revocation_statements': {'type': 'str'},
    'hanadb_username': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_hanadb",
        sdk_create=("DynamicSecretCreateHanaDb", "dynamic_secret_create_hana_db"),
        sdk_update=("DynamicSecretUpdateHanaDb", "dynamic_secret_update_hana_db"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
