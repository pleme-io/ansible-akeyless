#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_sectigo
short_description: Manages a Sectigo target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_sectigo resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_profile_id:
      description: "Certificate Profile ID in Sectigo account"
      type: int
      required: true
    customer_uri:
      description: "Customer Uri of the Sectigo account"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    external_requester:
      description: "External Requester - a comma separated list of emails"
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
    organization_id:
      description: "Organization ID in Sectigo account"
      type: int
      required: true
    timeout:
      description: "Timeout waiting for certificate validation in Duration format (1h - 1 Hour, 20m - 20 Minutes, 33m3s - 33 Minutes and 3 Seconds), maximum 1h."
      type: str
    password:
      description: "Password."
      type: str
      required: true
    username:
      description: "Username."
      type: str
      required: true

'''

EXAMPLES = r'''
- name: Create target_sectigo
  target_sectigo:
    state: present

- name: Delete target_sectigo
  target_sectigo:
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
    'certificate_profile_id': {'type': 'int', 'required': True},
    'customer_uri': {'type': 'str', 'required': True},
    'description': {'type': 'str'},
    'external_requester': {'type': 'str', 'required': True},
    'key': {'type': 'str', 'no_log': False},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password': {'type': 'str', 'required': True, 'no_log': True},
    'organization_id': {'type': 'int', 'required': True},
    'username': {'type': 'str', 'required': True},
    'timeout': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_sectigo',
        sdk_create=('TargetCreateSectigo', 'target_create_sectigo'),
        sdk_update=('TargetUpdateSectigo', 'target_update_sectigo'),
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
    )


if __name__ == '__main__':
    main()
