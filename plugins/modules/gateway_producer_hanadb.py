#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_hanadb
short_description: Manages a SAP HANA DB gateway producer (deprecated; prefer akeyless_dynamic_secret_hanadb)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_hanadb resources.
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
      description: "Protection from accidental deletion of this object [true/false]"
      type: str

    hana_dbname:
      description: "HanaDb Name"
      type: str
      required: true
    hanadb_create_statements:
      description: "HanaDb Creation statements"
      type: str

    hanadb_host:
      description: "HanaDb Host"
      type: str
      required: true

    hanadb_password:
      description: "HanaDb Password"
      type: str
      required: true
    hanadb_port:
      description: "HanaDb Port"
      type: str
    hanadb_revocation_statements:
      description: "HanaDb Revocation statements"
      type: str

    hanadb_username:
      description: "HanaDb Username"
      type: str
      required: true
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
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_hanadb
  gateway_producer_hanadb:
    state: present

- name: Delete gateway_producer_hanadb
  gateway_producer_hanadb:
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
    'delete_protection': {'type': 'str'},
    'hana_dbname': {'type': 'str', 'required': True},
    'hanadb_create_statements': {'type': 'str'},
    'hanadb_host': {'type': 'str', 'required': True},
    'hanadb_password': {'type': 'str', 'required': True, 'no_log': True},
    'hanadb_port': {'type': 'str'},
    'hanadb_revocation_statements': {'type': 'str'},
    'hanadb_username': {'type': 'str', 'required': True},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
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
        resource_label='gateway_producer_hanadb',
        sdk_create=('GatewayCreateProducerHanaDb', 'gateway_create_producer_hana_db'),
        sdk_update=('GatewayUpdateProducerHanaDb', 'gateway_update_producer_hana_db'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
