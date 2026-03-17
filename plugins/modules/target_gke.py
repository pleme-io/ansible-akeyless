#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_gke
short_description: Manages a Google GKE target in Akeyless Vault
description:
  - Manage target_gke resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    gke_account_key:
      description: "GCP service account key JSON (base64)"
      type: str
      no_log: true
    gke_cluster_cert:
      description: "GKE cluster CA certificate (PEM)"
      type: str
      no_log: true
    gke_cluster_endpoint:
      description: "GKE cluster API server URL"
      type: str
    gke_cluster_name:
      description: "GKE cluster name"
      type: str
    gke_service_account_email:
      description: "GCP service account email"
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
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_gke
  target_gke:
    state: present

- name: Delete target_gke
  target_gke:
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
        module.exit_json(changed=True, msg="target_gke created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_gke: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_gke updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_gke: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_gke deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_gke: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_gke: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'description': {'type': 'str'},
        'gke_account_key': {'type': 'str', 'no_log': True},
        'gke_cluster_cert': {'type': 'str', 'no_log': True},
        'gke_cluster_endpoint': {'type': 'str'},
        'gke_cluster_name': {'type': 'str'},
        'gke_service_account_email': {'type': 'str'},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'use_gw_cloud_identity': {'type': 'bool'},
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
            module.exit_json(changed=False, msg="target_gke already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
