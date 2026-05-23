#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_azure
short_description: Manages an Azure rotated secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage rotated_secret_azure resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_id:
      description: "API ID to rotate (relevant only for rotator-type=api-key)"
      type: str
    api_key:
      description: "API key to rotate (relevant only for rotator-type=api-key)"
      type: str
      no_log: true
    application_id:
      description: "Id of the azure app that hold the serect to be rotated (relevant only for rotator-type=api-key & authentication-credentials=use-target-creds)"
      type: str
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
    explicitly_set_sa:
      description: "If set, explicitly provide the storage account details [true/false]"
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
    resource_group_name:
      description: "The resource group name (only relevant when explicitly-set-sa=true)"
      type: str
    resource_name:
      description: "The name of the storage account (only relevant when explicitly-set-sa=true)"
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
    rotator_type:
      description: "The rotator type: target or api-key"
      type: str
      required: true
    storage_account_key_name:
      description: "The name of the storage account key to rotate [key1/key2/kerb1/kerb2] (relevat to azure-storage-account)"
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
- name: Create rotated_secret_azure
  rotated_secret_azure:
    state: present

- name: Delete rotated_secret_azure
  rotated_secret_azure:
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
    'api_id': {'type': 'str'},
    'api_key': {'type': 'str', 'no_log': True},
    'application_id': {'type': 'str'},
    'authentication_credentials': {'type': 'str'},
    'auto_rotate': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'explicitly_set_sa': {'type': 'str'},
    'grace_rotation': {'type': 'str'},
    'grace_rotation_hour': {'type': 'int'},
    'grace_rotation_interval': {'type': 'str'},
    'grace_rotation_timing': {'type': 'str'},
    'key': {'type': 'str'},
    'lock_during_sra_session': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'resource_group_name': {'type': 'str'},
    'resource_name': {'type': 'str'},
    'rotate_after_disconnect': {'type': 'str'},
    'rotation_event_in': {'type': 'list', 'elements': 'str'},
    'rotation_hour': {'type': 'int'},
    'rotation_interval': {'type': 'str'},
    'rotator_type': {'type': 'str', 'required': True},
    'storage_account_key_name': {'type': 'str'},
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
        resource_label="rotated_secret_azure",
        sdk_create=("RotatedSecretCreateAzure", "rotated_secret_create_azure"),
        sdk_update=("RotatedSecretUpdateAzure", "rotated_secret_update_azure"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
