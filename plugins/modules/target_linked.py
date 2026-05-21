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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("TargetCreateLinked", dict(module.params, token=token))
    return call_api(module, client, "target_create_linked", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateLinked", dict(module.params, token=token))
    return call_api(module, client, "target_update_linked", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("TargetDelete", dict(module.params, token=token))
    return call_api(module, client, "target_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("TargetGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "target_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'description': {'type': 'str'},
        'hosts': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'parent_target_name': {'type': 'str'},
        'type': {'type': 'str'},
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
        module.exit_json(changed=False, msg="target_linked already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
