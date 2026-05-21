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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("AccountCustomFieldCreate", dict(module.params, token=token))
    return call_api(module, client, "account_custom_field_create", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("AccountCustomFieldUpdate", dict(module.params, token=token))
    return call_api(module, client, "account_custom_field_update", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("AccountCustomFieldDelete", dict(module.params, token=token))
    return call_api(module, client, "account_custom_field_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("AccountCustomFieldGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "account_custom_field_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'name': {'type': 'str', 'required': True},
        'object': {'type': 'str', 'required': True},
        'object_type': {'type': 'str', 'required': True},
        'required': {'type': 'bool'},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="account_custom_field already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
