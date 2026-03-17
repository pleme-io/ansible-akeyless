#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_linked
short_description: Manages a linked target in Akeyless Vault
description:
  - Manage target_linked resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    hosts:
      description: "Hosts for the linked target"
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    parent_target_name:
      description: "Parent target name to link to"
      type: str
    type:
      description: "Specifies the hosts type, relevant only when working without parent target"
      type: str
'''

EXAMPLES = r'''
- name: Create target_linked
  target_linked:
    state: present

- name: Delete target_linked
  target_linked:
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
        module.exit_json(changed=True, msg="target_linked created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_linked: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_linked updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_linked: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_linked deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_linked: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_linked: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'description': {'type': 'str'},
        'hosts': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'parent_target_name': {'type': 'str'},
        'type': {'type': 'str'},
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
            module.exit_json(changed=False, msg="target_linked already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
