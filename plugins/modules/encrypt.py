#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: encrypt
short_description: Encrypt plaintext using an Akeyless key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Encrypt plaintext using an Akeyless key
options:
    display_id:
      description: "Display ID of the key"
      type: str
    encryption_context:
      description: "Authenticated-encryption context (key/value)"
      type: dict
    input_format:
      description: "Assumed format for plaintext input (e.g. base64)"
      type: str
    item_id:
      description: "Item ID of the key"
      type: int
    key_name:
      description: "Name of the key used for encryption"
      type: str
      required: true
    plaintext:
      description: "Data to be encrypted"
      type: str
    version:
      description: "Key version (classic keys only)"
      type: int
'''

EXAMPLES = r'''
- name: Run encrypt
  encrypt:
  register: result
'''

RETURN = r'''
result:
  description: "Raw result of the action call"
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("Encrypt", dict(module.params, token=token))
    return call_api(module, client, "encrypt", body)


def main():
    argument_spec = {
        'display_id': {'type': 'str'},
        'encryption_context': {'type': 'dict'},
        'input_format': {'type': 'str'},
        'item_id': {'type': 'int'},
        'key_name': {'type': 'str', 'required': True},
        'plaintext': {'type': 'str'},
        'version': {'type': 'int'},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'result'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
