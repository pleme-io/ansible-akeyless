#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_globalsign_atlas
short_description: Manages a GlobalSign Atlas target in Akeyless Vault
description:
  - Manage target_globalsign_atlas resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "GlobalSign Atlas API key"
      type: str
      required: true
      no_log: true
    api_secret:
      description: "GlobalSign Atlas API secret"
      type: str
      required: true
      no_log: true
    description:
      description: "Target description"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    mtls_cert_data_base64:
      description: "Mutual TLS Certificate contents of the GlobalSign Atlas account encoded in base64, either mtls-cert-file-path or mtls-cert-data-base64 must be supplied"
      type: str
    mtls_key_data_base64:
      description: "Mutual TLS Key contents of the GlobalSign Atlas account encoded in base64, either mtls-key-file-path or mtls-data-base64 must be supplied"
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    timeout:
      description: "Timeout waiting for certificate validation in Duration format (1h - 1 Hour, 20m - 20 Minutes, 33m3s - 33 Minutes and 3 Seconds), maximum 1h."
      type: str
'''

EXAMPLES = r'''
- name: Create target_globalsign_atlas
  target_globalsign_atlas:
    state: present

- name: Delete target_globalsign_atlas
  target_globalsign_atlas:
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
        module.exit_json(changed=True, msg="target_globalsign_atlas created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_globalsign_atlas: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_globalsign_atlas updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_globalsign_atlas: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_globalsign_atlas deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_globalsign_atlas: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_globalsign_atlas: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'api_key': {'type': 'str', 'required': True, 'no_log': True},
        'api_secret': {'type': 'str', 'required': True, 'no_log': True},
        'description': {'type': 'str'},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'mtls_cert_data_base64': {'type': 'str'},
        'mtls_key_data_base64': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'timeout': {'type': 'str'},
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
            module.exit_json(changed=False, msg="target_globalsign_atlas already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
