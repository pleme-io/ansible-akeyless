#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_k8s
short_description: Manages a Kubernetes target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_k8s resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    k8s_auth_type:
      description: "Kubernetes auth type: token, certificate, or password"
      type: str
    k8s_client_certificate:
      description: "Kubernetes client certificate (PEM)"
      type: str
    k8s_client_key:
      description: "Kubernetes client key (PEM)"
      type: str
    k8s_cluster_ca_cert:
      description: "Kubernetes cluster CA certificate (PEM)"
      type: str
    k8s_cluster_endpoint:
      description: "Kubernetes API server URL"
      type: str
    k8s_cluster_name:
      description: "K8S cluster name"
      type: str
    k8s_cluster_token:
      description: "Kubernetes bearer token"
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
    use_gw_service_account:
      description: "Use gateway service account for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_k8s
  target_k8s:
    state: present

- name: Delete target_k8s
  target_k8s:
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
    'k8s_auth_type': {'type': 'str'},
    'k8s_client_certificate': {'type': 'str', 'no_log': True},
    'k8s_client_key': {'type': 'str', 'no_log': True},
    'k8s_cluster_ca_cert': {'type': 'str', 'no_log': True},
    'k8s_cluster_endpoint': {'type': 'str'},
    'k8s_cluster_name': {'type': 'str'},
    'k8s_cluster_token': {'type': 'str', 'no_log': True},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'use_gw_service_account': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_k8s",
        sdk_create=("TargetCreateK8s", "target_create_k8s"),
        sdk_update=("TargetUpdateK8s", "target_update_k8s"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
