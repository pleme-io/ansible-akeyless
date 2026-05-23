#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: usc
short_description: Manages a universal secrets connector (USC) in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage usc resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    binary_value:
      description: "Use this option if the universal secrets value is a base64 encoded binary"
      type: bool
    description:
      description: "Description of the universal secrets"
      type: str
    namespace:
      description: "The namespace (relevant for Hashi vault target)"
      type: str
    object_type:
      description: ""
      type: str
    pfx_password:
      description: "Optional, the passphrase that protects the private key within the pfx certificate (Relevant only for Azure KV certificates)"
      type: str
    region:
      description: "Optional, create secret in a specific region (GCP only).
If empty, a global secret will be created (provider default)."
      type: str
    secret_name:
      description: "Name for the new universal secrets"
      type: str
      required: true
    selected_repositories:
      description: ""
      type: str
    tags:
      description: "Tags for the universal secrets"
      type: dict
    usc_encryption_key:
      description: "Optional, The name of the remote key that used to encrypt the secret value (if empty, the default key will be used)"
      type: str
    usc_name:
      description: "Name of the Universal Secrets Connector item"
      type: str
      required: true
    value:
      description: "Value of the universal secrets item, either text or base64 encoded binary"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create usc
  usc:
    state: present

- name: Delete usc
  usc:
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
    'binary_value': {'type': 'bool'},
    'description': {'type': 'str'},
    'namespace': {'type': 'str'},
    'object_type': {'type': 'str'},
    'pfx_password': {'type': 'str'},
    'region': {'type': 'str'},
    'secret_name': {'type': 'str', 'required': True},
    'selected_repositories': {'type': 'str'},
    'tags': {'type': 'dict'},
    'usc_encryption_key': {'type': 'str'},
    'usc_name': {'type': 'str', 'required': True},
    'value': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="usc",
        sdk_create=("UscCreate", "usc_create"),
        sdk_update=("UscUpdate", "usc_update"),
        sdk_delete=("UscDelete", "usc_delete"),
        sdk_read=("UscGet", "usc_get"),
    )


if __name__ == '__main__':
    main()
