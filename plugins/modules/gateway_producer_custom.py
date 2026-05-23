#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_custom
short_description: Manages a custom gateway producer (deprecated; prefer akeyless_dynamic_secret_custom)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_custom resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    admin_rotation_interval_days:
      description: "Define rotation interval in days"
      type: int
    create_sync_url:
      description: "URL of an endpoint that implements /sync/create method, for example
https://webhook.example.com/sync/create"
      type: str
      required: true
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    enable_admin_rotation:
      description: "Should admin credentials be rotated"
      type: bool
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    payload:
      description: "Secret payload to be sent with each create/revoke webhook request"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    revoke_sync_url:
      description: "URL of an endpoint that implements /sync/revoke method, for example
https://webhook.example.com/sync/revoke"
      type: str
      required: true
    rotate_sync_url:
      description: "URL of an endpoint that implements /sync/rotate method, for example
https://webhook.example.com/sync/rotate"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    timeout_sec:
      description: "Maximum allowed time in seconds for the webhook to return the results"
      type: int
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_custom
  gateway_producer_custom:
    state: present

- name: Delete gateway_producer_custom
  gateway_producer_custom:
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
    'admin_rotation_interval_days': {'type': 'int'},
    'create_sync_url': {'type': 'str', 'required': True},
    'delete_protection': {'type': 'str'},
    'enable_admin_rotation': {'type': 'bool'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'payload': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'revoke_sync_url': {'type': 'str', 'required': True},
    'rotate_sync_url': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'timeout_sec': {'type': 'int'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_producer_custom",
        sdk_create=("GatewayCreateProducerCustom", "gateway_create_producer_custom"),
        sdk_update=("GatewayUpdateProducerCustom", "gateway_update_producer_custom"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
