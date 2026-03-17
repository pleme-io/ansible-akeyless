#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: esm
short_description: Manages an external secrets manager (ESM) in Akeyless Vault
description:
  - Manage esm resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    binary_value:
      description: "Use this option if the external secret value is a base64 encoded binary"
      type: bool
    description:
      description: "Description of the external secret"
      type: str
    esm_name:
      description: "Name of the External Secrets Manager item"
      type: str
      required: true
    secret_name:
      description: "Name for the new external secret"
      type: str
      required: true
    tags:
      description: "Tags for the external secret"
      type: dict
    value:
      description: "Value of the external secret item, either text or base64 encoded binary"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create esm
  esm:
    state: present

- name: Delete esm
  esm:
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
        module.exit_json(changed=True, msg="esm created")
    except Exception as e:
        module.fail_json(msg="Failed to create esm: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="esm updated")
    except Exception as e:
        module.fail_json(msg="Failed to update esm: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="esm deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete esm: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read esm: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'binary_value': {'type': 'bool'},
        'description': {'type': 'str'},
        'esm_name': {'type': 'str', 'required': True},
        'secret_name': {'type': 'str', 'required': True},
        'tags': {'type': 'dict'},
        'value': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="esm already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
