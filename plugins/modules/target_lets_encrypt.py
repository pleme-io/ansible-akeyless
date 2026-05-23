#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_lets_encrypt
short_description: Manages a Let's Encrypt target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_lets_encrypt resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    acme_challenge:
      description: ""
      type: str
    description:
      description: "Target description"
      type: str
    dns_target_creds:
      description: "Name of existing cloud target for DNS credentials. Required when acme-challenge=dns. Supported: AWS, Azure, GCP targets"
      type: str

    email:
      description: "Email address for ACME account registration"
      type: str
      required: true
    gcp_project:
      description: "GCP Cloud DNS: Project ID. Optional - can be derived from service account"
      type: str
    hosted_zone:
      description: "AWS Route53 hosted zone ID. Required when dns-target-creds points to AWS target"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    lets_encrypt_url:
      description: ""
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    resource_group:
      description: "Azure resource group name. Required when dns-target-creds points to Azure target"
      type: str
    timeout:
      description: ""
      type: str
'''

EXAMPLES = r'''
- name: Create target_lets_encrypt
  target_lets_encrypt:
    state: present

- name: Delete target_lets_encrypt
  target_lets_encrypt:
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
    'acme_challenge': {'type': 'str'},
    'description': {'type': 'str'},
    'dns_target_creds': {'type': 'str'},
    'email': {'required': True, 'type': 'str'},
    'gcp_project': {'type': 'str'},
    'hosted_zone': {'type': 'str'},
    'key': {'type': 'str', 'no_log': False},
    'lets_encrypt_url': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'resource_group': {'type': 'str'},
    'timeout': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_lets_encrypt',
        sdk_create=('TargetCreateLetsEncrypt', 'target_create_lets_encrypt'),
        sdk_update=('TargetUpdateLetsEncrypt', 'target_update_lets_encrypt'),
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
    )


if __name__ == '__main__':
    main()
