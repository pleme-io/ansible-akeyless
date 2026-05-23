#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_ssh
short_description: Manages an SSH rotated secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage rotated_secret_ssh resources.
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
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    key:
      description: "Encryption key name for the secret value"
      type: str
    key_data_base64:
      description: "Private key file contents encoded using base64"
      type: str
      no_log: true
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
    public_key_remote_path:
      description: "Path to the public key that will be rotated on the server"
      type: str
    rotate_after_disconnect:
      description: "Rotate after SRA session ends [true/false]"
      type: str
    rotated_password:
      description: "Rotated-username password (relevant only for rotator-type=password)"
      type: str
      no_log: true
    rotated_username:
      description: "Username to be rotated"
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
    rotator_custom_cmd:
      description: "Custom rotation command"
      type: str
    rotator_type:
      description: "The rotator type: target, password, or key"
      type: str
      required: true
    same_password:
      description: "Rotate same password for each host from Linked Target"
      type: str
    secure_access_target_type:
      description: "Specify target type. Options are ssh or rdp"
      type: str
    tags:
      description: "Tags for the rotated secret"
      type: list
      elements: str
    target_name:
      description: "Target name to associate"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create rotated_secret_ssh
  rotated_secret_ssh:
    state: present

- name: Delete rotated_secret_ssh
  rotated_secret_ssh:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'key': {'type': 'str'},
    'key_data_base64': {'type': 'str', 'no_log': True},
    'lock_during_sra_session': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'public_key_remote_path': {'type': 'str'},
    'rotate_after_disconnect': {'type': 'str'},
    'rotated_password': {'type': 'str', 'no_log': True},
    'rotated_username': {'type': 'str'},
    'rotation_event_in': {'type': 'list', 'elements': 'str'},
    'rotation_hour': {'type': 'int'},
    'rotation_interval': {'type': 'str'},
    'rotator_custom_cmd': {'type': 'str'},
    'rotator_type': {'type': 'str', 'required': True},
    'same_password': {'type': 'str'},
    'secure_access_target_type': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="rotated_secret_ssh",
        sdk_create=("RotatedSecretCreateSsh", "rotated_secret_create_ssh"),
        sdk_update=("RotatedSecretUpdateSsh", "rotated_secret_update_ssh"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
