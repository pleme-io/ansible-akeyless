#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_aws
short_description: Manages an AWS target in Akeyless Vault
description:
  - Manage target_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_key:
      description: "AWS secret access key"
      type: str
      required: true
      no_log: true
    access_key_id:
      description: "AWS access key ID"
      type: str
      required: true
      no_log: true
    description:
      description: "Target description"
      type: str
    generate_external_id:
      description: "A unique auto-generated value used in your AWS account when configuring your AWS IAM role to securely delegate access to Akeyless. Relevant only when using GW cloud ID"
      type: bool
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
    region:
      description: "AWS region"
      type: str
    role_arn:
      description: "AWS IAM role identifier that Gateway will assume in your AWS account, relevant only when using external ID"
      type: str
    session_token:
      description: "AWS session token (for temporary credentials)"
      type: str
      no_log: true
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_aws
  target_aws:
    state: present

- name: Delete target_aws
  target_aws:
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
        module.exit_json(changed=True, msg="target_aws created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_aws: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_aws updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_aws: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_aws deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_aws: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_aws: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'access_key': {'type': 'str', 'required': True, 'no_log': True},
        'access_key_id': {'type': 'str', 'required': True, 'no_log': True},
        'description': {'type': 'str'},
        'generate_external_id': {'type': 'bool'},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'region': {'type': 'str'},
        'role_arn': {'type': 'str'},
        'session_token': {'type': 'str', 'no_log': True},
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
            module.exit_json(changed=False, msg="target_aws already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
