#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_linked
short_description: Manages a linked target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_linked",
        sdk_create=("TargetCreateLinked", "target_create_linked"),
        sdk_update=("TargetUpdateLinked", "target_update_linked"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
