#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_aws
short_description: Manages an AWS target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_key:
      description: "AWS secret access key"
      type: str
      required: true
    access_key_id:
      description: "AWS access key ID"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    generate_external_id:
      description: "A unique auto-generated value used in your AWS account when configuring your AWS IAM role to securely delegate access to Akeyless. Relevant only when using GW cloud ID"
      type: bool
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
    region:
      description: "AWS region"
      type: str
    role_arn:
      description: "AWS IAM role identifier that Gateway will assume in your AWS account, relevant only when using external ID"
      type: str
    session_token:
      description: "AWS session token (for temporary credentials)"
      type: str
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_aws
  target_aws:
    state: present

- name: Delete target_aws
  target_aws:
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
    'access_key': {'type': 'str', 'required': True, 'no_log': True},
    'access_key_id': {'type': 'str', 'required': True, 'no_log': True},
    'description': {'type': 'str'},
    'generate_external_id': {'type': 'bool'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'region': {'type': 'str'},
    'role_arn': {'type': 'str'},
    'session_token': {'type': 'str', 'no_log': True},
    'use_gw_cloud_identity': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_aws",
        sdk_create=("TargetCreateAws", "target_create_aws"),
        sdk_update=("TargetUpdateAws", "target_update_aws"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
