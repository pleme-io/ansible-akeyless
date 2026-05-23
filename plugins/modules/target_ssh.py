#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_ssh
short_description: Manages an SSH target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_ssh resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    host:
      description: "SSH host address"
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
    port:
      description: "SSH port (default: 22)"
      type: str
    private_key:
      description: "SSH private key (PEM)"
      type: str
    private_key_password:
      description: "SSH private key passphrase"
      type: str
    ssh_password:
      description: "SSH password"
      type: str
    ssh_username:
      description: "SSH username"
      type: str
'''

EXAMPLES = r'''
- name: Create target_ssh
  target_ssh:
    state: present

- name: Delete target_ssh
  target_ssh:
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
    'description': {'type': 'str'},
    'host': {'type': 'str'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'port': {'type': 'str'},
    'private_key': {'type': 'str', 'no_log': True},
    'private_key_password': {'type': 'str', 'no_log': True},
    'ssh_password': {'type': 'str', 'no_log': True},
    'ssh_username': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_ssh",
        sdk_create=("TargetCreateSsh", "target_create_ssh"),
        sdk_update=("TargetUpdateSsh", "target_update_ssh"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
