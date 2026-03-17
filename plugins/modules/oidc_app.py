#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: oidc_app
short_description: Manages an OIDC application in Akeyless Vault
description:
  - Manage oidc_app resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    accessibility:
      description: "for personal password manager"
      type: str
    audience:
      description: "A comma separated list of allowed audiences"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key:
      description: "The name of a key that used to encrypt the OIDC application (if empty, the account default protectionKey key will be used)"
      type: str
    name:
      description: "OIDC application name"
      type: str
      required: true
    permission_assignment:
      description: "A json string defining the access permission assignment for this app"
      type: str
    public:
      description: "Set to true if the app is public (cannot keep secrets)"
      type: bool
    redirect_uris:
      description: "A comma separated list of allowed redirect uris"
      type: str
    scopes:
      description: "A comma separated list of allowed scopes"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create oidc_app
  oidc_app:
    state: present

- name: Delete oidc_app
  oidc_app:
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
        module.exit_json(changed=True, msg="oidc_app created")
    except Exception as e:
        module.fail_json(msg="Failed to create oidc_app: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="oidc_app updated")
    except Exception as e:
        module.fail_json(msg="Failed to update oidc_app: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="oidc_app deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete oidc_app: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read oidc_app: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'accessibility': {'type': 'str'},
        'audience': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'key': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'permission_assignment': {'type': 'str'},
        'public': {'type': 'bool'},
        'redirect_uris': {'type': 'str'},
        'scopes': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
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
            module.exit_json(changed=False, msg="oidc_app already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
