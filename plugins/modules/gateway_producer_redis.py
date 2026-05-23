#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_redis
short_description: Manages a Redis gateway producer (deprecated; prefer akeyless_dynamic_secret_redis)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_redis resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present

    acl_rules:
      description: "A JSON array list of redis ACL rules to attach to the created user. For available rules see the ACL CAT command https://redis.io/commands/acl-cat
      type: str
By default the user will have permissions to read all keys '['~*', '+@read']'"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    host:
      description: "Redis Host"
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
    port:
      description: "Redis Port"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    ssl:
      description: "Enable/Disable SSL [true/false]"
      type: bool
    ssl_certificate:
      description: "SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA)"
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
- name: Create gateway_producer_redis
  gateway_producer_redis:
    state: present

- name: Delete gateway_producer_redis
  gateway_producer_redis:
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
    'acl_rules': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'host': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'port': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
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
        resource_label='gateway_producer_redis',
        sdk_create=('GatewayCreateProducerRedis', 'gateway_create_producer_redis'),
        sdk_update=('GatewayUpdateProducerRedis', 'gateway_update_producer_redis'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
