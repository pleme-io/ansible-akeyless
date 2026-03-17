#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_k8s
short_description: Manages a Kubernetes dynamic secret producer
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

from ansible.module_utils.basic import AnsibleModule


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_k8s created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_k8s: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_k8s updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_k8s: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_k8s deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_k8s: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_k8s: %s" % str(e))


def main():
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
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params.get('state', 'present')
    current = read_resource(module)

    if module.check_mode:
        module.exit_json(changed=(current is None and state == 'present')
                         or (current is not None and state == 'absent'))

    if state == 'absent':
        if current is not None:
            delete_resource(module)
        else:
            module.exit_json(changed=False, msg="dynamic_secret_k8s already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
