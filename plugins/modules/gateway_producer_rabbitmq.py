#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_rabbitmq
short_description: Manages a RabbitMQ gateway producer (deprecated; prefer akeyless_dynamic_secret_rabbitmq)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_rabbitmq resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
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
      description: "Server URI"
      type: str
      required: true

    rabbitmq_user_conf_permission:
      description: "User configuration permission"
      type: str
      required: true

    rabbitmq_user_read_permission:
      description: "User read permission"
      type: str
      required: true
    rabbitmq_user_tags:
      description: "User Tags"
      type: str
    rabbitmq_user_vhost:
      description: "User Virtual Host"
      type: str

    rabbitmq_user_write_permission:
      description: "User write permission"
      type: str
      required: true
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
- name: Create gateway_producer_rabbitmq
  gateway_producer_rabbitmq:
    state: present

- name: Delete gateway_producer_rabbitmq
  gateway_producer_rabbitmq:
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
    'delete_protection': {'type': 'str'},
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
        resource_label='gateway_producer_rabbitmq',
        sdk_create=('GatewayCreateProducerRabbitMQ', 'gateway_create_producer_rabbit_mq'),
        sdk_update=('GatewayUpdateProducerRabbitMQ', 'gateway_update_producer_rabbit_mq'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
