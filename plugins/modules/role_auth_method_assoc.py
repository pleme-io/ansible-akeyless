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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("AssocRoleAuthMethod", dict(module.params, token=token))
    return call_api(module, client, "assoc_role_auth_method", body)


def update_resource(module, client, token):
    """No-op: associations have no mutable fields. Re-applying a present
    state when the assoc already exists is idempotent (returns no-change)."""
    return None


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteRoleAssociation", dict(module.params, token=token))
    return call_api(module, client, "delete_role_association", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GetRole", {"name": module.params.get("role_name"), "token": token})
    return call_api(module, client, "get_role", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'am_name': {'type': 'str', 'required': True},
        'case_sensitive': {'type': 'str'},
        'role_name': {'type': 'str', 'required': True},
        'sub_claims': {'type': 'dict'},
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
        module.exit_json(changed=False, msg="role_auth_method_assoc already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        update_resource(module, client, token)
        module.exit_json(changed=False, msg="role_auth_method_assoc already present")


if __name__ == '__main__':
    main()
