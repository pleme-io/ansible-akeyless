#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_data_with_classic_key
short_description: Sign arbitrary data using a Classic key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_action_module,
)

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


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('SignDataWithClassicKey', 'sign_data_with_classic_key'),
    )


if __name__ == '__main__':
    main()
