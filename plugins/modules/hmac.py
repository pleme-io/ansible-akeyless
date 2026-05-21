#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hmac
short_description: Compute an HMAC using an Akeyless AES key
description:
  - Compute an HMAC using an Akeyless AES key
options:
    display_id:
      description: "Display ID of the key"
      type: str
    hash_function:
      description: "Hash function (sha-256 or sha-512)"
      type: str
    input_format:
      description: "Assumed format for plaintext input (e.g. base64)"
      type: str
    item_id:
      description: "Item ID of the key"
      type: int
    key_name:
      description: "Name of the AES key"
      type: str
      required: true
    plaintext:
      description: "Data to authenticate"
      type: str
'''

EXAMPLES = r'''
- name: Run hmac
  hmac:
  register: result
'''

RETURN = r'''
result:
  description: "Raw result of the action call"
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("Hmac", dict(module.params, token=token))
    return call_api(module, client, "hmac", body)


def main():
    argument_spec = {
        'display_id': {'type': 'str'},
        'hash_function': {'type': 'str'},
        'input_format': {'type': 'str'},
        'item_id': {'type': 'int'},
        'key_name': {'type': 'str', 'required': True},
        'plaintext': {'type': 'str'},
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
