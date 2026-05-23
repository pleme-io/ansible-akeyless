#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_windows
short_description: Manages a Windows target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_windows resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate:
      description: "Client certificate (PEM)"
      type: str
    connection_type:
      description: "Type of connection to Windows Server [credentials/parent-target]"
      type: str
    description:
      description: "Target description"
      type: str
    domain:
      description: "Windows domain"
      type: str
    hostname:
      description: "Windows host address"
      type: str
      required: true
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
    parent_target_name:
      description: "Name of the parent target, relevant only when connection-type is parent-target"
      type: str
    port:
      description: "WinRM port (default: 5986)"
      type: str
    use_tls:
      description: "Use TLS for WinRM connection"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_windows
  target_windows:
    state: present

- name: Delete target_windows
  target_windows:
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
    'certificate': {'type': 'str', 'no_log': True},
    'connection_type': {'type': 'str'},
    'description': {'type': 'str'},
    'domain': {'type': 'str'},
    'hostname': {'type': 'str', 'required': True},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'parent_target_name': {'type': 'str'},
    'port': {'type': 'str'},
    'use_tls': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_windows",
        sdk_create=("TargetCreateWindows", "target_create_windows"),
        sdk_update=("TargetUpdateWindows", "target_update_windows"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
