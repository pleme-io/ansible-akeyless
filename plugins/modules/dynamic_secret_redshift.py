#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_redshift
short_description: Manages a Redshift dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_redshift resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    creation_statements:
      description: "Redshift creation statements"
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
    producer_encryption_key:
      description: "Dynamic producer encryption key"
      type: str
    redshift_db_name:
      description: "Redshift DB Name"
      type: str
    redshift_host:
      description: "Redshift host"
      type: str
    redshift_password:
      description: "Redshift admin password"
      type: str
      no_log: true
    redshift_port:
      description: "Redshift port (default: 5439)"
      type: str
    redshift_username:
      description: "Redshift admin username"
      type: str
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
- name: Create dynamic_secret_redshift
  dynamic_secret_redshift:
    state: present

- name: Delete dynamic_secret_redshift
  dynamic_secret_redshift:
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
    'producer_encryption_key': {'type': 'str'},
    'redshift_db_name': {'type': 'str'},
    'redshift_host': {'type': 'str'},
    'redshift_password': {'type': 'str', 'no_log': True},
    'redshift_port': {'type': 'str'},
    'redshift_username': {'type': 'str'},
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
        resource_label="dynamic_secret_redshift",
        sdk_create=("DynamicSecretCreateRedshift", "dynamic_secret_create_redshift"),
        sdk_update=("DynamicSecretUpdateRedshift", "dynamic_secret_update_redshift"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
