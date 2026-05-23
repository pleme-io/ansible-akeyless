#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_postgresql
short_description: Manages a PostgreSQL dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_postgresql resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    creation_statements:
      description: "PostgreSQL creation statements"
      type: str
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
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    postgresql_db_name:
      description: "PostgreSQL DB Name"
      type: str
    postgresql_host:
      description: "PostgreSQL host"
      type: str
    postgresql_password:
      description: "PostgreSQL admin password"
      type: str
      no_log: true
    postgresql_port:
      description: "PostgreSQL port (default: 5432)"
      type: str
    postgresql_username:
      description: "PostgreSQL admin username"
      type: str
    producer_encryption_key:
      description: "Dynamic producer encryption key"
      type: str
    revocation_statement:
      description: "PostgreSQL Revocation statements"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    ssl:
      description: "Enable SSL connection"
      type: bool
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
- name: Create dynamic_secret_postgresql
  dynamic_secret_postgresql:
    state: present

- name: Delete dynamic_secret_postgresql
  dynamic_secret_postgresql:
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
    'creation_statements': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'postgresql_db_name': {'type': 'str'},
    'postgresql_host': {'type': 'str'},
    'postgresql_password': {'type': 'str', 'no_log': True},
    'postgresql_port': {'type': 'str'},
    'postgresql_username': {'type': 'str'},
    'producer_encryption_key': {'type': 'str'},
    'revocation_statement': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'ssl': {'type': 'bool'},
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
        resource_label="dynamic_secret_postgresql",
        sdk_create=("DynamicSecretCreatePostgreSql", "dynamic_secret_create_postgre_sql"),
        sdk_update=("DynamicSecretUpdatePostgreSql", "dynamic_secret_update_postgre_sql"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
