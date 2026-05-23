#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_eks
short_description: Manages an Amazon EKS target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_eks resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    eks_access_key_id:
      description: "AWS access key ID for EKS"
      type: str
      required: true
    eks_cluster_ca_cert:
      description: "EKS cluster CA certificate (PEM)"
      type: str
      required: true
    eks_cluster_endpoint:
      description: "EKS cluster API server URL"
      type: str
      required: true
    eks_cluster_name:
      description: "EKS cluster name"
      type: str
      required: true
    eks_region:
      description: "AWS region for EKS cluster"
      type: str
    eks_secret_access_key:
      description: "AWS secret access key for EKS"
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
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_eks
  target_eks:
    state: present

- name: Delete target_eks
  target_eks:
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
    'description': {'type': 'str'},
    'eks_access_key_id': {'type': 'str', 'required': True, 'no_log': True},
    'eks_cluster_ca_cert': {'type': 'str', 'required': True, 'no_log': True},
    'eks_cluster_endpoint': {'type': 'str', 'required': True},
    'eks_cluster_name': {'type': 'str', 'required': True},
    'eks_region': {'type': 'str'},
    'eks_secret_access_key': {'type': 'str', 'required': True, 'no_log': True},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'use_gw_cloud_identity': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_eks",
        sdk_create=("TargetCreateEks", "target_create_eks"),
        sdk_update=("TargetUpdateEks", "target_update_eks"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
