#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: static_secret
short_description: Manages a static secret in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage static_secret resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    accessibility:
      description: "Secret accessibility: regular or personal"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    format:
      description: "Secret format [text/json/key-value] (relevant only for type 'generic')"
      type: str
    lock_during_sra_session:
      description: "Lock this secret for read/update while an SRA session is active"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Secret name"
      type: str
      required: true
    protection_key:
      description: "Encryption key name for the secret"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    type:
      description: "The secret sub type [generic/password]"
      type: str
    value:
      description: "The secret value"
      type: str
      required: true
      no_log: true
'''

EXAMPLES = r'''
- name: Create static_secret
  static_secret:
    state: present

- name: Delete static_secret
  static_secret:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'format': {'type': 'str'},
    'lock_during_sra_session': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'protection_key': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'type': {'type': 'str'},
    'value': {'type': 'str', 'required': True, 'no_log': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="static_secret",
        sdk_create=("CreateSecret", "create_secret"),
        sdk_update=("UpdateSecretVal", "update_secret_val"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
