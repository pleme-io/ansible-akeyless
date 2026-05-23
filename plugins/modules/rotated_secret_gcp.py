#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_gcp
short_description: Manages a GCP rotated secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage rotated_secret_gcp resources.
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
    gcp_key:
      description: "Base64-encoded service account private key text"
      type: str
    gcp_service_account_email:
      description: "The email of the gcp service account to rotate"
      type: str
    gcp_service_account_key_id:
      description: "The key id of the gcp service account to rotate"
      type: str
    grace_rotation:
      description: "Enable graceful rotation (keep both versions temporarily). When enabled, a new secret version is created while the previous version is kept for the grace period, so both versions exist for a limited time. [true/false]"
      type: str
    grace_rotation_hour:
      description: "The Hour of the grace rotation in UTC"
      type: int
    grace_rotation_interval:
      description: "The number of days to wait before deleting the old key (must be bigger than rotation-interval)"
      type: str
    grace_rotation_timing:
      description: "When to create the new version relative to the rotation date [after/before]"
      type: str
    key:
      description: "Encryption key name for the secret value"
      type: str
    max_versions:
      description: "Maximum number of versions"
      type: str
    name:
      description: "Rotated secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
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
    rotator_type:
      description: "The rotator type: target or api-key"
      type: str
      required: true
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
- name: Create rotated_secret_gcp
  rotated_secret_gcp:
    state: present

- name: Delete rotated_secret_gcp
  rotated_secret_gcp:
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
    'gcp_key': {'type': 'str'},
    'gcp_service_account_email': {'type': 'str'},
    'gcp_service_account_key_id': {'type': 'str'},
    'grace_rotation': {'type': 'str'},
    'grace_rotation_hour': {'type': 'int'},
    'grace_rotation_interval': {'type': 'str'},
    'grace_rotation_timing': {'type': 'str'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'rotation_event_in': {'type': 'list', 'elements': 'str'},
    'rotation_hour': {'type': 'int'},
    'rotation_interval': {'type': 'str'},
    'rotator_type': {'type': 'str', 'required': True},
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
        resource_label="rotated_secret_gcp",
        sdk_create=("RotatedSecretCreateGcp", "rotated_secret_create_gcp"),
        sdk_update=("RotatedSecretUpdateGcp", "rotated_secret_update_gcp"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
