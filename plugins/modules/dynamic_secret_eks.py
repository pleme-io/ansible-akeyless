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
      required: true
    eks_assume_role:
      description: "AWS role ARN to assume for EKS"
      type: str

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
      required: true

    eks_secret_access_key:
      description: "AWS secret access key for EKS"
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("DynamicSecretCreateEks", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_create_eks", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("DynamicSecretUpdateEks", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_update_eks", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DynamicSecretDelete", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DynamicSecretGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "dynamic_secret_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'eks_access_key_id': {'type': 'str', 'no_log': True, 'required': True},
        'eks_assume_role': {'type': 'str'},
        'eks_cluster_ca_cert': {'type': 'str', 'no_log': True, 'required': True},
        'eks_cluster_endpoint': {'type': 'str', 'required': True},
        'eks_cluster_name': {'type': 'str', 'required': True, 'no_log': False},
        'eks_region': {'type': 'str', 'required': True},
        'eks_secret_access_key': {'type': 'str', 'no_log': True, 'required': True},
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="dynamic_secret_eks already absent")
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
        module.exit_json(changed=False, msg="dynamic_secret_eks already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
