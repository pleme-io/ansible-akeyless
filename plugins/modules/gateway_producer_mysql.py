#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_mysql
short_description: Manages a MySQL gateway producer (deprecated; prefer akeyless_dynamic_secret_mysql)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_mysql resources.
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

    mysql_dbname:
      description: "MySQL DB Name"
      type: str
      required: true

    mysql_host:
      description: "MySQL Host"
      type: str
      required: true

    mysql_password:
      description: "MySQL Password"
      type: str
      required: true
    mysql_port:
      description: "MySQL Port"
      type: str
    mysql_revocation_statements:
      description: "MySQL Revocation statements"
      type: str
    mysql_screation_statements:
      description: "MySQL Creation statements"
      type: str

    mysql_username:
      description: "MySQL Username"
      type: str
      required: true
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
      description: "Enable/Disable SSL [true/false]"
      type: bool
    ssl_certificate:
      description: "SSL connection certificate"
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
- name: Create gateway_producer_mysql
  gateway_producer_mysql:
    state: present

- name: Delete gateway_producer_mysql
  gateway_producer_mysql:
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
    'mysql_dbname': {'type': 'str', 'required': True},
    'mysql_host': {'type': 'str', 'required': True},
    'mysql_password': {'type': 'str', 'required': True, 'no_log': True},
    'mysql_port': {'type': 'str'},
    'mysql_revocation_statements': {'type': 'str'},
    'mysql_screation_statements': {'type': 'str'},
    'mysql_username': {'type': 'str', 'required': True},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'ssl': {'type': 'bool'},
    'ssl_certificate': {'type': 'str'},
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
        resource_label='gateway_producer_mysql',
        sdk_create=('GatewayCreateProducerMySQL', 'gateway_create_producer_my_sql'),
        sdk_update=('GatewayUpdateProducerMySQL', 'gateway_update_producer_my_sql'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
