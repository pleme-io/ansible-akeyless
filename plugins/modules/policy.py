#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: policy
short_description: Manages a policy in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage policy resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    allowed_algorithms:
      description: "Specify allowed key algorithms (e.g., [RSA2048,AES128GCM])"
      type: list
      elements: str
    allowed_key_names:
      description: "Specify allowed protection key names. To enforce using the account's default protection key, use 'default-account-key'"
      type: list
      elements: str
    allowed_key_types:
      description: "Specify allowed key protection types (dfc, classic-key)"
      type: list
      elements: str
    max_rotation_interval_days:
      description: "Set the maximum rotation interval for automatic key rotation."
      type: int
    object_types:
      description: "The object types this policy will apply to (items, targets). If not provided, defaults to [items, targets]."
      type: list
      elements: str
    path:
      description: "The path the policy refers to"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create policy
  policy:
    state: present

- name: Delete policy
  policy:
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
    'allowed_algorithms': {'type': 'list', 'elements': 'str'},
    'allowed_key_names': {'type': 'list', 'elements': 'str', 'no_log': False},
    'allowed_key_types': {'type': 'list', 'elements': 'str', 'no_log': False},
    'max_rotation_interval_days': {'type': 'int'},
    'object_types': {'type': 'list', 'elements': 'str'},
    'path': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='policy',
        sdk_create=('PolicyCreateKeys', 'policy_create_keys'),
        sdk_update=('PolicyUpdateKeys', 'policy_update_keys'),
        sdk_delete=('PoliciesDelete', 'policies_delete'),
        sdk_read=('PoliciesGet', 'policies_get'),
    )


if __name__ == '__main__':
    main()
