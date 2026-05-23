#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_custom
short_description: Manages a custom dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_custom resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    admin_rotation_interval_days:
      description: "Admin credentials rotation interval in days"
      type: int
    create_sync_url:
      description: "URL to call on create/sync"
      type: str
      required: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    enable_admin_rotation:
      description: "Enable admin credentials rotation"
      type: bool
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    payload:
      description: "Custom payload to send to the URL"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    revoke_sync_url:
      description: "URL to call on revoke"
      type: str
      required: true
    rotate_sync_url:
      description: "URL to call on rotate"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    timeout_sec:
      description: "Timeout in seconds for custom calls"
      type: int
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_custom
  dynamic_secret_custom:
    state: present

- name: Delete dynamic_secret_custom
  dynamic_secret_custom:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
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
        resource_label='dynamic_secret_custom',
        sdk_create=('DynamicSecretCreateCustom', 'dynamic_secret_create_custom'),
        sdk_update=('DynamicSecretUpdateCustom', 'dynamic_secret_update_custom'),
        sdk_delete=('DynamicSecretDelete', 'dynamic_secret_delete'),
        sdk_read=('DynamicSecretGet', 'dynamic_secret_get'),
    )


if __name__ == '__main__':
    main()
