#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_sectigo
short_description: Manages a Sectigo target in Akeyless Vault
description:
  - Manage target_sectigo resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_profile_id:
      description: "Certificate Profile ID in Sectigo account"
      type: int
      required: true
    customer_uri:
      description: "Customer Uri of the Sectigo account"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    external_requester:
      description: "External Requester - a comma separated list of emails"
      type: str
      required: true
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
    organization_id:
      description: "Organization ID in Sectigo account"
      type: int
      required: true
    timeout:
      description: "Timeout waiting for certificate validation in Duration format (1h - 1 Hour, 20m - 20 Minutes, 33m3s - 33 Minutes and 3 Seconds), maximum 1h."
      type: str
'''

EXAMPLES = r'''
- name: Create target_sectigo
  target_sectigo:
    state: present

- name: Delete target_sectigo
  target_sectigo:
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
        module.exit_json(changed=True, msg="target_sectigo created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_sectigo: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_sectigo updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_sectigo: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_sectigo deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_sectigo: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_sectigo: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'certificate_profile_id': {'type': 'int', 'required': True},
        'customer_uri': {'type': 'str', 'required': True},
        'description': {'type': 'str'},
        'external_requester': {'type': 'str', 'required': True},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'organization_id': {'type': 'int', 'required': True},
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
            module.exit_json(changed=False, msg="target_sectigo already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
