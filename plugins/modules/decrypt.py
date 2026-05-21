#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: decrypt
short_description: Decrypt ciphertext using an Akeyless key
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("Decrypt", dict(module.params, token=token))
    return call_api(module, client, "decrypt", body)


def main():
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

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'result'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
