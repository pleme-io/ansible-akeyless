#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: decrypt
short_description: Decrypt ciphertext using an Akeyless key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Decrypt ciphertext using an Akeyless key
options:
    ciphertext:
      description: "Base64-encoded ciphertext to decrypt"
      type: str
    display_id:
      description: "Display ID of the key"
      type: str
    encryption_context:
      description: "Authenticated-encryption context (must match encrypt-side context)"
      type: dict
    item_id:
      description: "Item ID of the key"
      type: int
    key_name:
      description: "Name of the key used for decryption"
      type: str
      required: true
    output_format:
      description: "Output format (e.g. base64)"
      type: str
    version:
      description: "Key version (classic keys only)"
      type: int
'''

EXAMPLES = r'''
- name: Run decrypt
  decrypt:
  register: result
'''

RETURN = r'''
result:
  description: "Raw result of the action call"
  type: dict
  returned: success
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_action_module,
)

argument_spec = {
    'ciphertext': {'type': 'str'},
    'display_id': {'type': 'str'},
    'encryption_context': {'type': 'dict'},
    'item_id': {'type': 'int'},
    'key_name': {'type': 'str', 'required': True},
    'output_format': {'type': 'str'},
    'version': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("Decrypt", "decrypt"),
    )


if __name__ == '__main__':
    main()
