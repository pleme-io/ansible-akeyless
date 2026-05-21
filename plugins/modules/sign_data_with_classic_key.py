#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_data_with_classic_key
short_description: Sign arbitrary data using a Classic key
description:
  - Sign arbitrary data using a Classic key
options:
    data:
      description: "Data to sign"
      type: str
      required: true
    display_id:
      description: "Display name of the classic key"
      type: str
      required: true
    hashed:
      description: "Whether the data is already hashed"
      type: bool
    hashing_method:
      description: "Hashing method (default: SHA256)"
      type: str
    ignore_cache:
      description: "Bypass the Gateway secret cache (true/false string)"
      type: str
    name:
      description: "Classic key name"
      type: str
      required: true
    version:
      description: "Classic key version"
      type: int
      required: true
'''

EXAMPLES = r'''
- name: Run sign_data_with_classic_key
  sign_data_with_classic_key:
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
    body = build_body("SignDataWithClassicKey", dict(module.params, token=token))
    return call_api(module, client, "sign_data_with_classic_key", body)


def main():
    argument_spec = {
        'data': {'type': 'str', 'required': True},
        'display_id': {'type': 'str', 'required': True},
        'hashed': {'type': 'bool'},
        'hashing_method': {'type': 'str'},
        'ignore_cache': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'version': {'type': 'int', 'required': True},
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
