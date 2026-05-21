#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_ecdsa
short_description: Sign a message using an ECDSA key
description:
  - Sign a message using an ECDSA key
options:
    accessibility:
      description: "Item accessibility (default: regular)"
      type: str
    display_id:
      description: "Display ID of the EC key"
      type: str
    item_id:
      description: "Item ID of the EC key"
      type: int
    key_name:
      description: "Name of the EC key"
      type: str
    message:
      description: "Base64-encoded message to sign"
      type: str
      required: true
    prehashed:
      description: "Whether the message is already hashed"
      type: bool
    version:
      description: "Key version"
      type: int
'''

EXAMPLES = r'''
- name: Run sign_ecdsa
  sign_ecdsa:
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
    body = build_body("SignEcDsa", dict(module.params, token=token))
    return call_api(module, client, "sign_ec_dsa", body)


def main():
    argument_spec = {
        'accessibility': {'type': 'str'},
        'display_id': {'type': 'str'},
        'item_id': {'type': 'int'},
        'key_name': {'type': 'str'},
        'message': {'type': 'str', 'required': True},
        'prehashed': {'type': 'bool'},
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
