#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_globalsign
short_description: Manages a GlobalSign target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_globalsign resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    contact_email:
      description: "Contact email"
      type: str
      required: true
    contact_first_name:
      description: "Contact first name"
      type: str
      required: true
    contact_last_name:
      description: "Contact last name"
      type: str
      required: true
    contact_phone:
      description: "Contact phone number"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    profile_id:
      description: "GlobalSign profile ID"
      type: str
      required: true
    timeout:
      description: "Timeout waiting for certificate validation in Duration format (1h - 1 Hour, 20m - 20 Minutes, 33m3s - 33 Minutes and 3 Seconds), maximum 1h."
      type: str
    password:
      description: "Password."
      type: str
      required: true
    username:
      description: "Username."
      type: str
      required: true

'''

EXAMPLES = r'''
- name: Create target_globalsign
  target_globalsign:
    state: present

- name: Delete target_globalsign
  target_globalsign:
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
    'contact_email': {'type': 'str', 'required': True},
    'contact_first_name': {'type': 'str', 'required': True},
    'contact_last_name': {'type': 'str', 'required': True},
    'contact_phone': {'type': 'str', 'required': True},
    'description': {'type': 'str'},
    'key': {'type': 'str', 'no_log': False},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password': {'type': 'str', 'required': True, 'no_log': True},
    'profile_id': {'type': 'str', 'required': True},
    'username': {'type': 'str', 'required': True},
    'timeout': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_globalsign',
        sdk_create=('TargetCreateGlobalSign', 'target_create_global_sign'),
        sdk_update=('TargetUpdateGlobalSign', 'target_update_global_sign'),
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
    )


if __name__ == '__main__':
    main()
