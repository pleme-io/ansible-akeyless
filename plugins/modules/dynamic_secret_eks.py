#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_eks
short_description: Manages an Amazon EKS dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_eks resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    eks_access_key_id:
      description: "AWS access key ID for EKS"
      type: str
      no_log: true
    eks_assume_role:
      description: "AWS role ARN to assume for EKS"
      type: str
    eks_cluster_ca_cert:
      description: "EKS cluster CA certificate (PEM)"
      type: str
      no_log: true
    eks_cluster_endpoint:
      description: "EKS cluster API server URL"
      type: str
    eks_cluster_name:
      description: "EKS cluster name"
      type: str
    eks_region:
      description: "AWS region for EKS cluster"
      type: str
    eks_secret_access_key:
      description: "AWS secret access key for EKS"
      type: str
      no_log: true
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    secure_access_allow_port_forwading:
      description: "Enable Port forwarding while using CLI access"
      type: bool
    secure_access_cluster_endpoint:
      description: "The K8s cluster endpoint URL"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_eks
  dynamic_secret_eks:
    state: present

- name: Delete dynamic_secret_eks
  dynamic_secret_eks:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'eks_access_key_id': {'type': 'str', 'no_log': True},
    'eks_assume_role': {'type': 'str'},
    'eks_cluster_ca_cert': {'type': 'str', 'no_log': True},
    'eks_cluster_endpoint': {'type': 'str'},
    'eks_cluster_name': {'type': 'str'},
    'eks_region': {'type': 'str'},
    'eks_secret_access_key': {'type': 'str', 'no_log': True},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_allow_port_forwading': {'type': 'bool'},
    'secure_access_cluster_endpoint': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_eks",
        sdk_create=("DynamicSecretCreateEks", "dynamic_secret_create_eks"),
        sdk_update=("DynamicSecretUpdateEks", "dynamic_secret_update_eks"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
