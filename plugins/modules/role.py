#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role
short_description: Manages a role in Akeyless Vault
description:
  - Manage role resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    analytics_access:
      description: "Allow this role to view analytics"
      type: str
    audit_access:
      description: "Allow this role to view audit logs"
      type: str
    comment:
      description: "Deprecated - use description"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Role description"
      type: str
    event_center_access:
      description: "Allow this role to view Event Center. Currently only 'none', 'scoped' and 'all'
values are supported"
      type: str
    event_forwarders_access:
      description: "Allow this role to manage Event Forwarders. Currently only 'none' and 'all' values are supported."
      type: str
    event_forwarders_name:
      description: "Allow this role to manage the following Event Forwarders."
      type: list
      elements: str
    gw_analytics_access:
      description: "Allow this role to view gateway analytics"
      type: str
    name:
      description: "Role name"
      type: str
      required: true
    reverse_rbac_access:
      description: "Allow this role to view Reverse RBAC. Supported values: 'scoped', 'all'."
      type: str
    sra_reports_access:
      description: "Allow this role to view SRA reports"
      type: str
    usage_reports_access:
      description: "Allow this role to view Usage Report. Currently only 'none' and
'all' values are supported."
      type: str
'''

EXAMPLES = r'''
- name: Create role
  role:
    state: present

- name: Delete role
  role:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("CreateRole", dict(module.params, token=token))
    return call_api(module, client, "create_role", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdateRole", dict(module.params, token=token))
    return call_api(module, client, "update_role", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteRole", dict(module.params, token=token))
    return call_api(module, client, "delete_role", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GetRole", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "get_role", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'analytics_access': {'type': 'str'},
        'audit_access': {'type': 'str'},
        'comment': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'description': {'type': 'str'},
        'event_center_access': {'type': 'str'},
        'event_forwarders_access': {'type': 'str'},
        'event_forwarders_name': {'type': 'list', 'elements': 'str'},
        'gw_analytics_access': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'reverse_rbac_access': {'type': 'str'},
        'sra_reports_access': {'type': 'str'},
        'usage_reports_access': {'type': 'str'},
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
        module.exit_json(changed=False, msg="role already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
