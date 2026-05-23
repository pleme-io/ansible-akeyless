#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_mssql
short_description: Manages an MSSQL dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_mssql resources.
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
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    mssql_allowed_db_names:
      description: "CSV of allowed DB names for runtime selection when getting the secret value.
Empty => use target DB only; '*' => any DB allowed; One or more names => user must choose from this list"
      type: str
    mssql_create_statements:
      description: "MSSQL Creation statements"
      type: str
    mssql_dbname:
      description: "MSSQL database name"
      type: str
    mssql_host:
      description: "MSSQL host"
      type: str
    mssql_password:
      description: "MSSQL admin password"
      type: str
    mssql_port:
      description: "MSSQL port (default: 1433)"
      type: str
    mssql_revocation_statements:
      description: "MSSQL revocation statements"
      type: str
    mssql_username:
      description: "MSSQL admin username"
      type: str
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
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
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
- name: Create dynamic_secret_mssql
  dynamic_secret_mssql:
    state: present

- name: Delete dynamic_secret_mssql
  dynamic_secret_mssql:
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
    'item_custom_fields': {'type': 'dict'},
    'mssql_allowed_db_names': {'type': 'str'},
    'mssql_create_statements': {'type': 'str'},
    'mssql_dbname': {'type': 'str'},
    'mssql_host': {'type': 'str'},
    'mssql_password': {'type': 'str', 'no_log': True},
    'mssql_port': {'type': 'str'},
    'mssql_revocation_statements': {'type': 'str'},
    'mssql_username': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
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
        resource_label="dynamic_secret_mssql",
        sdk_create=("DynamicSecretCreateMsSql", "dynamic_secret_create_ms_sql"),
        sdk_update=("DynamicSecretUpdateMsSql", "dynamic_secret_update_ms_sql"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
