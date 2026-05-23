#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_rdp
short_description: Manages an RDP dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_rdp resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    allow_user_extend_session:
      description: "AllowUserExtendSession"
      type: int
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (relevant only for fixed-user-only=true)"
      type: str
    fixed_user_only:
      description: "Allow access using externally (IdP) provided username [true/false]"
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

    rdp_admin_name:
      description: "RDP admin username"
      type: str
      required: true

    rdp_admin_pwd:
      description: "RDP admin password"
      type: str
      required: true

    rdp_host_name:
      description: "RDP host address"
      type: str
      required: true
    rdp_host_port:
      description: "RDP port (default: 3389)"
      type: str

    rdp_user_groups:
      description: "RDP user groups for dynamic users"
      type: str
      required: true
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    secure_access_rd_gateway_server:
      description: "RD Gateway server"
      type: str
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
    warn_user_before_expiration:
      description: "WarnBeforeUserExpiration"
      type: int
'''

EXAMPLES = r'''
- name: Create dynamic_secret_rdp
  dynamic_secret_rdp:
    state: present

- name: Delete dynamic_secret_rdp
  dynamic_secret_rdp:
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
    'allow_user_extend_session': {'type': 'int'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'fixed_user_claim_keyname': {'type': 'str', 'no_log': False},
    'fixed_user_only': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'producer_encryption_key_name': {'type': 'str'},
    'rdp_admin_name': {'type': 'str', 'required': True},
    'rdp_admin_pwd': {'type': 'str', 'no_log': True, 'required': True},
    'rdp_host_name': {'type': 'str', 'required': True},
    'rdp_host_port': {'type': 'str'},
    'rdp_user_groups': {'type': 'str', 'required': True},
    'secure_access_delay': {'type': 'int'},
    'secure_access_rd_gateway_server': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'warn_user_before_expiration': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='dynamic_secret_rdp',
        sdk_create=('DynamicSecretCreateRdp', 'dynamic_secret_create_rdp'),
        sdk_update=('DynamicSecretUpdateRdp', 'dynamic_secret_update_rdp'),
        sdk_delete=('DynamicSecretDelete', 'dynamic_secret_delete'),
        sdk_read=('DynamicSecretGet', 'dynamic_secret_get'),
    )


if __name__ == '__main__':
    main()
