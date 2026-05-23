#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_custom
short_description: Manages a custom rotated secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage rotated_secret_custom resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    authentication_credentials:
      description: "Credentials to connect with: use-user-creds or use-target-creds"
      type: str
    auto_rotate:
      description: "Whether to automatically rotate every rotation-interval days [true/false]"
      type: str
    custom_payload:
      description: "Secret payload to be sent with rotation request"
      type: str
      no_log: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    enable_password_policy:
      description: "Enable password policy"
      type: str
    key:
      description: "Encryption key name for the secret value"
      type: str
    lock_during_sra_session:
      description: "Lock this secret for read/update while an SRA session is active"
      type: str
    max_versions:
      description: "Maximum number of versions"
      type: str
    name:
      description: "Rotated secret name"
      type: str
      required: true
    password_length:
      description: "Length of the password to be generated"
      type: str
    rotate_after_disconnect:
      description: "Rotate after SRA session ends [true/false]"
      type: str
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_hour:
      description: "The hour of the rotation in UTC"
      type: int
    rotation_interval:
      description: "Days between every automatic key rotation (1-365)"
      type: str
    tags:
      description: "Tags for the rotated secret"
      type: list
      elements: str
    target_name:
      description: "Target name to associate"
      type: str
      required: true
    timeout_sec:
      description: "Maximum allowed time in seconds for the custom rotator to return the results"
      type: int
    use_capital_letters:
      description: "Password must contain capital letters [true/false]"
      type: str
    use_lower_letters:
      description: "Password must contain lower case letters [true/false]"
      type: str
    use_numbers:
      description: "Password must contain numbers [true/false]"
      type: str
    use_special_characters:
      description: "Password must contain special characters [true/false]"
      type: str
'''

EXAMPLES = r'''
- name: Create rotated_secret_custom
  rotated_secret_custom:
    state: present

- name: Delete rotated_secret_custom
  rotated_secret_custom:
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
    'authentication_credentials': {'type': 'str'},
    'auto_rotate': {'type': 'str'},
    'custom_payload': {'type': 'str', 'no_log': True},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'enable_password_policy': {'type': 'str'},
    'key': {'type': 'str'},
    'lock_during_sra_session': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'rotate_after_disconnect': {'type': 'str'},
    'rotation_event_in': {'type': 'list', 'elements': 'str'},
    'rotation_hour': {'type': 'int'},
    'rotation_interval': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str', 'required': True},
    'timeout_sec': {'type': 'int'},
    'use_capital_letters': {'type': 'str'},
    'use_lower_letters': {'type': 'str'},
    'use_numbers': {'type': 'str'},
    'use_special_characters': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="rotated_secret_custom",
        sdk_create=("RotatedSecretCreateCustom", "rotated_secret_create_custom"),
        sdk_update=("RotatedSecretUpdateCustom", "rotated_secret_update_custom"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
