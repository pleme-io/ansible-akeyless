#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_ssh
short_description: Manages an SSH rotated secret
description:
  - Manage rotated_secret_ssh resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    authentication_credentials:
      description: "Credentials to connect with: use-user-creds or use-target-creds"
      type: str
    auto_rotate:
      description: "Whether to automatically rotate every rotation-interval days [true/false]"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    key:
      description: "Encryption key name for the secret value"
      type: str
    key_data_base64:
      description: "Private key file contents encoded using base64"
      type: str
      no_log: true
    max_versions:
      description: "Maximum number of versions"
      type: str
    name:
      description: "Rotated secret name"
      type: str
      required: true
    password_length:
      description: "Length of the password to be generated"
      type: str
    public_key_remote_path:
      description: "Path to the public key that will be rotated on the server"
      type: str
    rotate_after_disconnect:
      description: "Rotate after SRA session ends [true/false]"
      type: str
    rotated_password:
      description: "Rotated-username password (relevant only for rotator-type=password)"
      type: str
      no_log: true
    rotated_username:
      description: "Username to be rotated"
      type: str
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_hour:
      description: "The hour of the rotation in UTC"
      type: int
    rotation_interval:
      description: "Days between every automatic key rotation (1-365)"
      type: str
    rotator_custom_cmd:
      description: "Custom rotation command"
      type: str
    rotator_type:
      description: "The rotator type: target, password, or key"
      type: str
      required: true
    same_password:
      description: "Rotate same password for each host from Linked Target"
      type: str
    secure_access_target_type:
      description: "Specify target type. Options are ssh or rdp"
      type: str
    tags:
      description: "Tags for the rotated secret"
      type: list
      elements: str
    target_name:
      description: "Target name to associate"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create rotated_secret_ssh
  rotated_secret_ssh:
    state: present

- name: Delete rotated_secret_ssh
  rotated_secret_ssh:
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
        module.exit_json(changed=True, msg="rotated_secret_ssh created")
    except Exception as e:
        module.fail_json(msg="Failed to create rotated_secret_ssh: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="rotated_secret_ssh updated")
    except Exception as e:
        module.fail_json(msg="Failed to update rotated_secret_ssh: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="rotated_secret_ssh deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete rotated_secret_ssh: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read rotated_secret_ssh: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'authentication_credentials': {'type': 'str'},
        'auto_rotate': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'key': {'type': 'str'},
        'key_data_base64': {'type': 'str', 'no_log': True},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'public_key_remote_path': {'type': 'str'},
        'rotate_after_disconnect': {'type': 'str'},
        'rotated_password': {'type': 'str', 'no_log': True},
        'rotated_username': {'type': 'str'},
        'rotation_event_in': {'type': 'list', 'elements': 'str'},
        'rotation_hour': {'type': 'int'},
        'rotation_interval': {'type': 'str'},
        'rotator_custom_cmd': {'type': 'str'},
        'rotator_type': {'type': 'str', 'required': True},
        'same_password': {'type': 'str'},
        'secure_access_target_type': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="rotated_secret_ssh already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
