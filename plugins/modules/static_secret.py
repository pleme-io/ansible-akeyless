#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: static_secret
short_description: Manages a static secret in Akeyless Vault
description:
  - Manage static_secret resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    accessibility:
      description: "Secret accessibility: regular or personal"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    format:
      description: "Secret format [text/json/key-value] (relevant only for type 'generic')"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Secret name"
      type: str
      required: true
    protection_key:
      description: "Encryption key name for the secret"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    type:
      description: "The secret sub type [generic/password]"
      type: str
    value:
      description: "The secret value"
      type: str
      required: true
      no_log: true
'''

EXAMPLES = r'''
- name: Create static_secret
  static_secret:
    state: present

- name: Delete static_secret
  static_secret:
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
        module.exit_json(changed=True, msg="static_secret created")
    except Exception as e:
        module.fail_json(msg="Failed to create static_secret: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="static_secret updated")
    except Exception as e:
        module.fail_json(msg="Failed to update static_secret: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="static_secret deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete static_secret: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read static_secret: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'accessibility': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'format': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'protection_key': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'type': {'type': 'str'},
        'value': {'type': 'str', 'required': True, 'no_log': True},
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
            module.exit_json(changed=False, msg="static_secret already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
