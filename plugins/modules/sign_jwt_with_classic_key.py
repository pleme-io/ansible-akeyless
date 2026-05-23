#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_jwt_with_classic_key
short_description: Sign a JWT using a Classic key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_action_module,
)

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


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("SignJWTWithClassicKey", "sign_jwt_with_classic_key"),
    )


if __name__ == '__main__':
    main()
