#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_oracle
short_description: Manages an Oracle dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_oracle resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    db_server_certificates:
      description: "Database server certificates (PEM)"
      type: str
    db_server_name:
      description: "Database server name for TLS verification"
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
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    oracle_host:
      description: "Oracle host"
      type: str
    oracle_password:
      description: "Oracle admin password"
      type: str
    oracle_port:
      description: "Oracle port (default: 1521)"
      type: str
    oracle_revocation_statements:
      description: "Oracle revocation statements"
      type: str
    oracle_screation_statements:
      description: "Oracle Creation statements"
      type: str
    oracle_service_name:
      description: "Oracle service name"
      type: str
    oracle_username:
      description: "Oracle admin username"
      type: str
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
- name: Create dynamic_secret_oracle
  dynamic_secret_oracle:
    state: present

- name: Delete dynamic_secret_oracle
  dynamic_secret_oracle:
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
    'db_server_certificates': {'type': 'str', 'no_log': True},
    'db_server_name': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'oracle_host': {'type': 'str'},
    'oracle_password': {'type': 'str', 'no_log': True},
    'oracle_port': {'type': 'str'},
    'oracle_revocation_statements': {'type': 'str'},
    'oracle_screation_statements': {'type': 'str'},
    'oracle_service_name': {'type': 'str'},
    'oracle_username': {'type': 'str'},
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
        resource_label="dynamic_secret_oracle",
        sdk_create=("DynamicSecretCreateOracleDb", "dynamic_secret_create_oracle_db"),
        sdk_update=("DynamicSecretUpdateOracleDb", "dynamic_secret_update_oracle_db"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
