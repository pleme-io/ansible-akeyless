#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_azure
short_description: Manages an Azure target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_azure resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    azure_cloud:
      description: "Azure cloud environment to use. Values: AzureCloud (default), AzureUSGovernment, AzureChinaCloud."
      type: str
    client_id:
      description: "Azure client/application ID"
      type: str
    client_secret:
      description: "Azure client secret"
      type: str
    connection_type:
      description: "Type of connection [credentials/cloud-identity]"
      type: str
    description:
      description: "Target description"
      type: str
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
    resource_group_name:
      description: "Azure resource group name"
      type: str
    resource_name:
      description: "Azure resource name"
      type: str
    subscription_id:
      description: "Azure subscription ID"
      type: str
    tenant_id:
      description: "Azure tenant ID"
      type: str
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_azure
  target_azure:
    state: present

- name: Delete target_azure
  target_azure:
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
    'azure_cloud': {'type': 'str'},
    'client_id': {'type': 'str'},
    'client_secret': {'type': 'str', 'no_log': True},
    'connection_type': {'type': 'str'},
    'description': {'type': 'str'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'resource_group_name': {'type': 'str'},
    'resource_name': {'type': 'str'},
    'subscription_id': {'type': 'str'},
    'tenant_id': {'type': 'str'},
    'use_gw_cloud_identity': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_azure",
        sdk_create=("TargetCreateAzure", "target_create_azure"),
        sdk_update=("TargetUpdateAzure", "target_update_azure"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
