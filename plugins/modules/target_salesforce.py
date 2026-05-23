#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_salesforce
short_description: Manages a Salesforce target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_salesforce resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    app_private_key_data:
      description: "Base64 encoded PEM of the connected app private key (relevant for JWT auth only)"
      type: str
    auth_flow:
      description: "Salesforce auth flow: user-password or jwt-bearer"
      type: str
      required: true
    ca_cert_data:
      description: "Base64 encoded PEM cert to use when uploading a new key to Salesforce"
      type: str
    ca_cert_name:
      description: "name of the certificate in Salesforce tenant to use when uploading new key"
      type: str
    client_id:
      description: "Salesforce connected app client ID"
      type: str
      required: true
    client_secret:
      description: "Salesforce connected app client secret"
      type: str
      no_log: true
    description:
      description: "Target description"
      type: str
    email:
      description: "The email of the user attached to the oauth2 app used for connecting to Salesforce"
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
    security_token:
      description: "Salesforce security token"
      type: str
      no_log: true
    tenant_url:
      description: "Salesforce tenant URL"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create target_salesforce
  target_salesforce:
    state: present

- name: Delete target_salesforce
  target_salesforce:
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
    'app_private_key_data': {'type': 'str'},
    'auth_flow': {'type': 'str', 'required': True},
    'ca_cert_data': {'type': 'str'},
    'ca_cert_name': {'type': 'str'},
    'client_id': {'type': 'str', 'required': True},
    'client_secret': {'type': 'str', 'no_log': True},
    'description': {'type': 'str'},
    'email': {'type': 'str', 'required': True},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'security_token': {'type': 'str', 'no_log': True},
    'tenant_url': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_salesforce",
        sdk_create=("TargetCreateSalesforce", "target_create_salesforce"),
        sdk_update=("TargetUpdateSalesforce", "target_update_salesforce"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
