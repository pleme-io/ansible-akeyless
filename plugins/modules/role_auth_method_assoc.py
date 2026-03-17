#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role_auth_method_assoc
short_description: Manages a role-to-auth-method association in Akeyless Vault
description:
  - Manage role_auth_method_assoc resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    am_name:
      description: "Auth method name to associate with the role"
      type: str
      required: true
    case_sensitive:
      description: "Case-sensitive sub-claims matching"
      type: str
    role_name:
      description: "Role name to associate"
      type: str
      required: true
    sub_claims:
      description: "Sub-claims for the association (key=value pairs)"
      type: dict
'''

EXAMPLES = r'''
- name: Create role_auth_method_assoc
  role_auth_method_assoc:
    state: present

- name: Delete role_auth_method_assoc
  role_auth_method_assoc:
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
        module.exit_json(changed=True, msg="role_auth_method_assoc created")
    except Exception as e:
        module.fail_json(msg="Failed to create role_auth_method_assoc: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - am_name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="role_auth_method_assoc updated")
    except Exception as e:
        module.fail_json(msg="Failed to update role_auth_method_assoc: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="role_auth_method_assoc deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete role_auth_method_assoc: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read role_auth_method_assoc: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'am_name': {'type': 'str', 'required': True},
        'case_sensitive': {'type': 'str'},
        'role_name': {'type': 'str', 'required': True},
        'sub_claims': {'type': 'dict'},
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
            module.exit_json(changed=False, msg="role_auth_method_assoc already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
