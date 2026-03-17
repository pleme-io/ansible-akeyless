#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role_rule
short_description: Manages a role rule in Akeyless Vault
description:
  - Manage role_rule resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    capability:
      description: "Permission capability: read, create, update, delete, list, deny"
      type: list
      required: true
      elements: str
    path:
      description: "Item path the rule applies to"
      type: str
      required: true
    role_name:
      description: "Role name to attach the rule to"
      type: str
      required: true
    rule_type:
      description: "Rule type: item-rule or auth-method-rule or role-rule"
      type: str
    ttl:
      description: "RoleRule ttl"
      type: int
'''

EXAMPLES = r'''
- name: Create role_rule
  role_rule:
    state: present

- name: Delete role_rule
  role_rule:
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
        module.exit_json(changed=True, msg="role_rule created")
    except Exception as e:
        module.fail_json(msg="Failed to create role_rule: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - capability
    #   - path
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="role_rule updated")
    except Exception as e:
        module.fail_json(msg="Failed to update role_rule: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="role_rule deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete role_rule: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read role_rule: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'capability': {'type': 'list', 'required': True, 'elements': 'str'},
        'path': {'type': 'str', 'required': True},
        'role_name': {'type': 'str', 'required': True},
        'rule_type': {'type': 'str'},
        'ttl': {'type': 'int'},
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
            module.exit_json(changed=False, msg="role_rule already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
