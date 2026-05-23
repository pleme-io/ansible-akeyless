#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role
short_description: Manages a role in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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
      type: str
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
      type: str
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='role',
        sdk_create=('CreateRole', 'create_role'),
        sdk_update=('UpdateRole', 'update_role'),
        sdk_delete=('DeleteRole', 'delete_role'),
        sdk_read=('GetRole', 'get_role'),
    )


if __name__ == '__main__':
    main()
