#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: oidc_app
short_description: Manages an OIDC application in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="oidc_app",
        sdk_create=("CreateOidcApp", "create_oidc_app"),
        sdk_update=("UpdateOidcApp", "update_oidc_app"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
