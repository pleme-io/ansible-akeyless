#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_k8s
short_description: Manages a Kubernetes target in Akeyless Vault
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
      no_log: true
    k8s_client_key:
      description: "Kubernetes client key (PEM)"
      type: str
      no_log: true
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("TargetCreateK8s", dict(module.params, token=token))
    return call_api(module, client, "target_create_k8s", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateK8s", dict(module.params, token=token))
    return call_api(module, client, "target_update_k8s", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("TargetDelete", dict(module.params, token=token))
    return call_api(module, client, "target_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("TargetGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "target_get", body, swallow_404=True)


def main():
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="target_k8s already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
