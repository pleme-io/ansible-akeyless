#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_mongo
short_description: Manages a MongoDB gateway producer (deprecated; prefer akeyless_dynamic_secret_mongodb)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_mongo resources.
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
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    mongodb_atlas_api_private_key:
      description: "MongoDB Atlas private key"
      type: str
    mongodb_atlas_api_public_key:
      description: "MongoDB Atlas public key"
      type: str
    mongodb_atlas_project_id:
      description: "MongoDB Atlas project ID"
      type: str
    mongodb_custom_data:
      description: "MongoDB custom data"
      type: str
    mongodb_default_auth_db:
      description: "MongoDB server default authentication database"
      type: str

    mongodb_host_port:
      description: "MongoDB server host and port"
      type: str
      required: true

    mongodb_name:
      description: "MongoDB Name"
      type: str
      required: true

    mongodb_password:
      description: "MongoDB server password. You will prompted to provide a password if it will not appear in CLI parameters"
      type: str
      required: true
    mongodb_roles:
      description: "MongoDB Roles"
      type: str
    mongodb_scopes:
      description: "MongoDB Scopes (Atlas only)"
      type: str
    mongodb_server_uri:
      description: "MongoDB server URI"
      type: str
    mongodb_uri_options:
      description: "MongoDB server URI options"
      type: str

    mongodb_username:
      description: "MongoDB server username"
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
      description: "Encrypt producer with following key"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
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
- name: Create gateway_producer_mongo
  gateway_producer_mongo:
    state: present

- name: Delete gateway_producer_mongo
  gateway_producer_mongo:
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
    'item_custom_fields': {'type': 'dict'},
    'mongodb_atlas_api_private_key': {'type': 'str', 'no_log': True},
    'mongodb_atlas_api_public_key': {'type': 'str'},
    'mongodb_atlas_project_id': {'type': 'str'},
    'mongodb_custom_data': {'type': 'str'},
    'mongodb_default_auth_db': {'type': 'str'},
    'mongodb_host_port': {'type': 'str', 'required': True},
    'mongodb_name': {'type': 'str', 'required': True},
    'mongodb_password': {'type': 'str', 'required': True, 'no_log': True},
    'mongodb_roles': {'type': 'str'},
    'mongodb_scopes': {'type': 'str'},
    'mongodb_server_uri': {'type': 'str'},
    'mongodb_uri_options': {'type': 'str'},
    'mongodb_username': {'type': 'str', 'required': True},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
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
        resource_label='gateway_producer_mongo',
        sdk_create=('GatewayCreateProducerMongo', 'gateway_create_producer_mongo'),
        sdk_update=('GatewayUpdateProducerMongo', 'gateway_update_producer_mongo'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
