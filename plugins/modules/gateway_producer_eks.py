#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_eks
short_description: Manages an EKS gateway producer (deprecated; prefer akeyless_dynamic_secret_eks)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_eks resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str

    eks_access_key_id:
      description: "Access Key ID"
      type: str
      required: true
    eks_assume_role:
      description: "IAM assume role"
      type: str

    eks_cluster_ca_cert:
      description: "EKS cluster CA certificate"
      type: str
      required: true

    eks_cluster_endpoint:
      description: "EKS cluster URL endpoint"
      type: str
      required: true

    eks_cluster_name:
      description: "EKS cluster name"
      type: str
      required: true

    eks_region:
      description: "Region"
      type: str
      required: true

    eks_secret_access_key:
      description: "Secret Access Key"
      type: str
      required: true
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
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_eks
  gateway_producer_eks:
    state: present

- name: Delete gateway_producer_eks
  gateway_producer_eks:
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
    'delete_protection': {'type': 'str'},
    'eks_access_key_id': {'type': 'str', 'required': True},
    'eks_assume_role': {'type': 'str'},
    'eks_cluster_ca_cert': {'type': 'str', 'required': True},
    'eks_cluster_endpoint': {'type': 'str', 'required': True},
    'eks_cluster_name': {'type': 'str', 'required': True, 'no_log': False},
    'eks_region': {'type': 'str', 'required': True},
    'eks_secret_access_key': {'type': 'str', 'required': True, 'no_log': True},
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
        resource_label='gateway_producer_eks',
        sdk_create=('GatewayCreateProducerEks', 'gateway_create_producer_eks'),
        sdk_update=('GatewayUpdateProducerEks', 'gateway_update_producer_eks'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
