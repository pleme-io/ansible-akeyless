#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_jwt_with_classic_key
short_description: Sign a JWT using a Classic key
description:
  - Sign a JWT using a Classic key
options:
    display_id:
      description: "Name (or display ID) of the classic key"
      type: str
      required: true
    jwt_claims:
      description: "JWT claims payload"
      type: str
      required: true
    signing_method:
      description: "JWT signing method"
      type: str
      required: true
    version:
      description: "Classic key version"
      type: int
      required: true
'''

EXAMPLES = r'''
- name: Run sign_jwt_with_classic_key
  sign_jwt_with_classic_key:
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
    body = build_body("SignJWTWithClassicKey", dict(module.params, token=token))
    return call_api(module, client, "sign_jwt_with_classic_key", body)


def main():
    argument_spec = {
        'display_id': {'type': 'str', 'required': True},
        'jwt_claims': {'type': 'str', 'required': True},
        'signing_method': {'type': 'str', 'required': True},
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
