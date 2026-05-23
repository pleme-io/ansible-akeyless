#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: verify_pkcs1
short_description: Verify an RSA PKCS#1 v1.5 signature
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Verify an RSA PKCS#1 v1.5 signature
options:
    display_id:
      description: "Display ID of the key"
      type: str
    hash_function:
      description: "Hash function (e.g. sha-256)"
      type: str
    input_format:
      description: "Assumed format for plaintext (e.g. base64)"
      type: str
    item_id:
      description: "Item ID of the key"
      type: int
    key_name:
      description: "Name of the RSA key"
      type: str
      required: true
    message:
      description: "Message to verify"
      type: str
      required: true
    prehashed:
      description: "Whether the message is already hashed"
      type: bool
    signature:
      description: "Signature to verify"
      type: str
      required: true
    version:
      description: "Key version"
      type: int
'''

EXAMPLES = r'''
- name: Run verify_pkcs1
  verify_pkcs1:
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
    'display_id': {'type': 'str'},
    'hash_function': {'type': 'str'},
    'input_format': {'type': 'str'},
    'item_id': {'type': 'int'},
    'key_name': {'type': 'str', 'required': True},
    'message': {'type': 'str', 'required': True},
    'prehashed': {'type': 'bool'},
    'signature': {'type': 'str', 'required': True},
    'version': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("VerifyPKCS1", "verify_pkcs1"),
    )


if __name__ == '__main__':
    main()
