#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_mysql
short_description: Manages a MySQL dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_mysql resources.
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
      no_log: true
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
    mysql_dbname:
      description: "MySQL database name"
      type: str
    mysql_host:
      description: "MySQL host"
      type: str
    mysql_password:
      description: "MySQL admin password"
      type: str
      no_log: true
    mysql_port:
      description: "MySQL port (default: 3306)"
      type: str
    mysql_revocation_statements:
      description: "MySQL revocation statements"
      type: str
    mysql_screation_statements:
      description: "MySQL Creation statements"
      type: str
    mysql_username:
      description: "MySQL admin username"
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
    ssl:
      description: "Enable SSL connection"
      type: bool
    ssl_certificate:
      description: "SSL certificate (PEM)"
      type: str
      no_log: true
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
- name: Create dynamic_secret_mysql
  dynamic_secret_mysql:
    state: present

- name: Delete dynamic_secret_mysql
  dynamic_secret_mysql:
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
    'mysql_dbname': {'type': 'str'},
    'mysql_host': {'type': 'str'},
    'mysql_password': {'type': 'str', 'no_log': True},
    'mysql_port': {'type': 'str'},
    'mysql_revocation_statements': {'type': 'str'},
    'mysql_screation_statements': {'type': 'str'},
    'mysql_username': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'ssl': {'type': 'bool'},
    'ssl_certificate': {'type': 'str', 'no_log': True},
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
        resource_label="dynamic_secret_mysql",
        sdk_create=("DynamicSecretCreateMySql", "dynamic_secret_create_my_sql"),
        sdk_update=("DynamicSecretUpdateMySql", "dynamic_secret_update_my_sql"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
