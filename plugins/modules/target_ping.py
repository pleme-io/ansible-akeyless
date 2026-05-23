#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_ping
short_description: Manages a Ping Identity target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_ping resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    administrative_port:
      description: "Ping Identity administrative port"
      type: str
    authorization_port:
      description: "Ping Identity authorization port"
      type: str
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

    ping_url:
      description: "Ping Identity server URL"
      type: str
      required: true

    privileged_user:
      description: "Ping Identity privileged username"
      type: str
      required: true
    password:
      description: "Password."
      type: str
      required: true

'''

EXAMPLES = r'''
- name: Create target_ping
  target_ping:
    state: present

- name: Delete target_ping
  target_ping:
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
    'administrative_port': {'type': 'str'},
    'authorization_port': {'type': 'str'},
    'description': {'type': 'str'},
    'key': {'type': 'str', 'no_log': False},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password': {'type': 'str', 'no_log': True, 'required': True},
    'ping_url': {'type': 'str', 'required': True},
    'privileged_user': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_ping',
        sdk_create=('TargetCreatePing', 'target_create_ping'),
        sdk_update=('TargetUpdatePing', 'target_update_ping'),
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
    )


if __name__ == '__main__':
    main()
