#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: group
short_description: Manages a group in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage group resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Description of the group"
      type: str
    group_alias:
      description: "A short group alias"
      type: str
      required: true
    name:
      description: "Group name"
      type: str
      required: true
    user_assignment:
      description: "JSON string defining access permission assignment"
      type: str
'''

EXAMPLES = r'''
- name: Create group
  group:
    state: present

- name: Delete group
  group:
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
    'description': {'type': 'str'},
    'group_alias': {'type': 'str', 'required': True},
    'name': {'type': 'str', 'required': True},
    'user_assignment': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='group',
        sdk_create=('CreateGroup', 'create_group'),
        sdk_update=('UpdateGroup', 'update_group'),
        sdk_delete=('DeleteGroup', 'delete_group'),
        sdk_read=('GetGroup', 'get_group'),
    )


if __name__ == '__main__':
    main()
