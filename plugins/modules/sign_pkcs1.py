#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sign_pkcs1
short_description: Sign a hashed message using RSASSA-PKCS1 v1.5
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Sign a hashed message using RSASSA-PKCS1 v1.5
options:
    display_id:
      description: "Display ID of the key"
      type: str
    hash_function:
      description: "Hash function (e.g. sha-256)"
      type: str
    input_format:
      description: "Format assumed for the plaintext message (e.g. base64)"
      type: str
    item_id:
      description: "Item ID of the key"
      type: int

    key_name:
      description: "Name of the RSA key"
      type: str
      required: true
    payload:
      description: "Hashed message to sign"
      type: str
      required: true
    prehashed:
      description: "Markes that the message is already hashed"
      type: bool
    version:
      description: "Key version"
      type: int
'''

EXAMPLES = r'''
- name: Run sign_pkcs1
  sign_pkcs1:
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
    # argspec field is `payload` (avoid Ansible-reserved `message`);
    # remap to the SDK model\'s `message` field name.
    _p = dict(module.params, token=token)
    _p["message"] = _p.pop("payload", None)
    body = build_body("SignPKCS1", _p)
    return call_api(module, client, "sign_pkcs1", body)


def main():
    argument_spec = {
        'display_id': {'type': 'str'},
        'hash_function': {'type': 'str'},
        'input_format': {'type': 'str'},
        'item_id': {'type': 'int'},
        'key_name': {'type': 'str', 'required': True},
        'payload': {'type': 'str', 'required': True},
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
