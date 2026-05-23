#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_k8s
short_description: Manages a native Kubernetes gateway producer (deprecated; prefer akeyless_dynamic_secret_k8s)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_k8s resources.
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
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    k8s_allowed_namespaces:
      description: "Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic)"
      type: str

    k8s_cluster_ca_cert:
      description: "K8S cluster CA certificate"
      type: str
      required: true

    k8s_cluster_endpoint:
      description: "K8S cluster URL endpoint"
      type: str
      required: true
    k8s_cluster_name:
      description: "K8S cluster name"
      type: str

    k8s_cluster_token:
      description: "K8S cluster Bearer token"
      type: str
      required: true
    k8s_namespace:
      description: "K8S Namespace where the ServiceAccount exists."
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
      description: "K8S ServiceAccount to extract token from."
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
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    use_gw_service_account:
      description: "Use the GW's service account"
      type: bool
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_k8s
  gateway_producer_k8s:
    state: present

- name: Delete gateway_producer_k8s
  gateway_producer_k8s:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayCreateProducerNativeK8S", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_native_k8_s", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerNativeK8S", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_native_k8_s", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'k8s_allowed_namespaces': {'type': 'str'},
        'k8s_cluster_ca_cert': {'type': 'str', 'required': True},
        'k8s_cluster_endpoint': {'type': 'str', 'required': True},
        'k8s_cluster_name': {'type': 'str', 'no_log': False},
        'k8s_cluster_token': {'type': 'str', 'required': True, 'no_log': True},
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="gateway_producer_k8s already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        result = delete_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # state == 'present'
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = create_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs
    # from what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False, msg="gateway_producer_k8s already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
