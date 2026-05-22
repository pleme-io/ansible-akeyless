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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("SetRoleRule", dict(module.params, token=token))
    return call_api(module, client, "set_role_rule", body)


def update_resource(module, client, token):
    """No-op: role rules are content-addressable; re-applying the same
    rule is idempotent (returns no-change)."""
    return None


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteRoleRule", dict(module.params, token=token))
    return call_api(module, client, "delete_role_rule", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GetRole", {"name": module.params.get("role_name"), "token": token})
    return call_api(module, client, "get_role", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'capability': {'type': 'list', 'required': True, 'elements': 'str'},
        'path': {'type': 'str', 'required': True},
        'role_name': {'type': 'str', 'required': True},
        'rule_type': {'type': 'str'},
        'ttl': {'type': 'int'},
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
        module.exit_json(changed=False, msg="role_rule already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        update_resource(module, client, token)
        module.exit_json(changed=False, msg="role_rule already present")


if __name__ == '__main__':
    main()
