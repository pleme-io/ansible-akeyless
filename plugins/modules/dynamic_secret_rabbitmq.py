#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_rabbitmq
short_description: Manages a RabbitMQ dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_rabbitmq resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
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
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str

    rabbitmq_admin_pwd:
      description: "RabbitMQ Admin password"
      type: str
      required: true

    rabbitmq_admin_user:
      description: "RabbitMQ Admin User"
      type: str
      required: true

    rabbitmq_server_uri:
      description: "RabbitMQ management API URI"
      type: str
      required: true

    rabbitmq_user_conf_permission:
      description: "RabbitMQ configure permission for dynamic users"
      type: str
      required: true

    rabbitmq_user_read_permission:
      description: "RabbitMQ read permission for dynamic users"
      type: str
      required: true
    rabbitmq_user_tags:
      description: "RabbitMQ tags for dynamic users (comma-separated)"
      type: str
    rabbitmq_user_vhost:
      description: "RabbitMQ vhost for dynamic users"
      type: str

    rabbitmq_user_write_permission:
      description: "RabbitMQ write permission for dynamic users"
      type: str
      required: true
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
- name: Create dynamic_secret_rabbitmq
  dynamic_secret_rabbitmq:
    state: present

- name: Delete dynamic_secret_rabbitmq
  dynamic_secret_rabbitmq:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'producer_encryption_key_name': {'type': 'str'},
    'rabbitmq_admin_pwd': {'type': 'str', 'required': True},
    'rabbitmq_admin_user': {'type': 'str', 'required': True},
    'rabbitmq_server_uri': {'type': 'str', 'required': True},
    'rabbitmq_user_conf_permission': {'type': 'str', 'required': True},
    'rabbitmq_user_read_permission': {'type': 'str', 'required': True},
    'rabbitmq_user_tags': {'type': 'str'},
    'rabbitmq_user_vhost': {'type': 'str'},
    'rabbitmq_user_write_permission': {'type': 'str', 'required': True},
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
        resource_label='dynamic_secret_rabbitmq',
        sdk_create=('DynamicSecretCreateRabbitMq', 'dynamic_secret_create_rabbit_mq'),
        sdk_update=('DynamicSecretUpdateRabbitMq', 'dynamic_secret_update_rabbit_mq'),
        sdk_delete=('DynamicSecretDelete', 'dynamic_secret_delete'),
        sdk_read=('DynamicSecretGet', 'dynamic_secret_get'),
    )


if __name__ == '__main__':
    main()
