#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: account_custom_field
short_description: Manages an account custom field in Akeyless Vault
description:
  - Manage account_custom_field resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    name:
      description: "The name of the custom field"
      type: str
      required: true
    object:
      description: "The object to create the custom field"
      type: str
      required: true
    object_type:
      description: "The object type to create the custom field [e.g. STATIC_SECRET,DYNAMIC_SECRET,ROTATED_SECRET]"
      type: str
      required: true
    required:
      description: "Specify whether the custom field is mandatory"
      type: bool
'''

EXAMPLES = r'''
- name: Create account_custom_field
  account_custom_field:
    state: present

- name: Delete account_custom_field
  account_custom_field:
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
        module.exit_json(changed=True, msg="account_custom_field created")
    except Exception as e:
        module.fail_json(msg="Failed to create account_custom_field: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="account_custom_field updated")
    except Exception as e:
        module.fail_json(msg="Failed to update account_custom_field: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="account_custom_field deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete account_custom_field: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read account_custom_field: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'name': {'type': 'str', 'required': True},
        'object': {'type': 'str', 'required': True},
        'object_type': {'type': 'str', 'required': True},
        'required': {'type': 'bool'},
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
            module.exit_json(changed=False, msg="account_custom_field already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
