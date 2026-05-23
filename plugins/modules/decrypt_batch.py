#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: decrypt_batch
short_description: Decrypt multiple items in a single batched call
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Decrypt multiple items in a single batched call
options:
    context:
      description: "Encryption context per-line"
      type: dict
    data:
      description: "Base64-encoded ciphertext data (per-line)"
      type: str
    item_id:
      description: "Item ID of the key (per-line)"
      type: int
    item_version:
      description: "Key version (per-line)"
      type: int
'''

EXAMPLES = r'''
- name: Run decrypt_batch
  decrypt_batch:
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
    body = build_body("BatchEncryptionRequestLine", dict(module.params, token=token))
    return call_api(module, client, "decrypt_batch", body)


def main():
    argument_spec = {
        'context': {'type': 'dict'},
        'data': {'type': 'str'},
        'item_id': {'type': 'int'},
        'item_version': {'type': 'int'},
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
