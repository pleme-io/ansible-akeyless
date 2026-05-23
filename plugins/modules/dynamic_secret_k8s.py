#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_k8s
short_description: Manages a Kubernetes dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_k8s resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    k8s_allowed_namespaces:
      description: "Allowed Kubernetes namespaces (comma-separated)"
      type: str
    k8s_cluster_ca_cert:
      description: "Kubernetes cluster CA certificate (PEM)"
      type: str
      no_log: true
    k8s_cluster_endpoint:
      description: "Kubernetes API server URL"
      type: str
    k8s_cluster_name:
      description: "K8S cluster name"
      type: str
    k8s_cluster_token:
      description: "Kubernetes bearer token"
      type: str
      no_log: true
    k8s_namespace:
      description: "Kubernetes namespace"
      type: str
    k8s_predefined_role_name:
      description: "The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic)"
      type: str
    k8s_predefined_role_type:
      description: "Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic)"
      type: str
    k8s_rolebinding_yaml_data:
      description: "Content of the yaml in a Base64 format."
      type: str
    k8s_rolebinding_yaml_def:
      description: "Path to yaml file that contains definitions of K8S role and role binding (relevant only for k8s-service-account-type=dynamic)"
      type: str
    k8s_service_account:
      description: "Kubernetes service account name"
      type: str
    k8s_service_account_type:
      description: "K8S ServiceAccount type [fixed, dynamic]."
      type: str
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
    secure_access_dashboard_url:
      description: "The K8s dashboard url"
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
    use_gw_service_account:
      description: "Use the GW's service account"
      type: bool
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_k8s
  dynamic_secret_k8s:
    state: present

- name: Delete dynamic_secret_k8s
  dynamic_secret_k8s:
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
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'k8s_allowed_namespaces': {'type': 'str'},
    'k8s_cluster_ca_cert': {'type': 'str', 'no_log': True},
    'k8s_cluster_endpoint': {'type': 'str'},
    'k8s_cluster_name': {'type': 'str'},
    'k8s_cluster_token': {'type': 'str', 'no_log': True},
    'k8s_namespace': {'type': 'str'},
    'k8s_predefined_role_name': {'type': 'str'},
    'k8s_predefined_role_type': {'type': 'str'},
    'k8s_rolebinding_yaml_data': {'type': 'str'},
    'k8s_rolebinding_yaml_def': {'type': 'str'},
    'k8s_service_account': {'type': 'str'},
    'k8s_service_account_type': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_allow_port_forwading': {'type': 'bool'},
    'secure_access_cluster_endpoint': {'type': 'str'},
    'secure_access_dashboard_url': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'use_gw_service_account': {'type': 'bool'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_k8s",
        sdk_create=("DynamicSecretCreateK8s", "dynamic_secret_create_k8s"),
        sdk_update=("DynamicSecretUpdateK8s", "dynamic_secret_update_k8s"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
