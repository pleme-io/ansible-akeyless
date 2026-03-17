#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_ssh
short_description: Manages an SSH target in Akeyless Vault
description:
  - Manage target_ssh resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    host:
      description: "SSH host address"
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
    port:
      description: "SSH port (default: 22)"
      type: str
    private_key:
      description: "SSH private key (PEM)"
      type: str
      no_log: true
    private_key_password:
      description: "SSH private key passphrase"
      type: str
      no_log: true
    ssh_password:
      description: "SSH password"
      type: str
      no_log: true
    ssh_username:
      description: "SSH username"
      type: str
'''

EXAMPLES = r'''
- name: Create target_ssh
  target_ssh:
    state: present

- name: Delete target_ssh
  target_ssh:
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
        module.exit_json(changed=True, msg="target_ssh created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_ssh: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_ssh updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_ssh: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_ssh deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_ssh: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_ssh: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'description': {'type': 'str'},
        'host': {'type': 'str'},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'port': {'type': 'str'},
        'private_key': {'type': 'str', 'no_log': True},
        'private_key_password': {'type': 'str', 'no_log': True},
        'ssh_password': {'type': 'str', 'no_log': True},
        'ssh_username': {'type': 'str'},
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
            module.exit_json(changed=False, msg="target_ssh already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
