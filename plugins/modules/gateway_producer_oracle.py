#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_oracle
short_description: Manages an Oracle DB gateway producer (deprecated; prefer akeyless_dynamic_secret_oracle)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_oracle resources.
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
      description: "(Optional) DB server certificates"
      type: str
    db_server_name:
      description: "(Optional) Server name for certificate verification"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    oracle_host:
      description: "Oracle Host"
      type: str
    oracle_password:
      description: "Oracle Password"
      type: str
    oracle_port:
      description: "Oracle Port"
      type: str
    oracle_revocation_statements:
      description: "Oracle Revocation statements"
      type: str
    oracle_screation_statements:
      description: "Oracle Creation statements"
      type: str
    oracle_service_name:
      description: "Oracle DB Name"
      type: str
    oracle_username:
      description: "Oracle Username"
      type: str
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
- name: Create gateway_producer_oracle
  gateway_producer_oracle:
    state: present

- name: Delete gateway_producer_oracle
  gateway_producer_oracle:
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
    'db_server_certificates': {'type': 'str'},
    'db_server_name': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'oracle_host': {'type': 'str'},
    'oracle_password': {'type': 'str'},
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
        resource_label="gateway_producer_oracle",
        sdk_create=("GatewayCreateProducerOracleDb", "gateway_create_producer_oracle_db"),
        sdk_update=("GatewayUpdateProducerOracleDb", "gateway_update_producer_oracle_db"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
