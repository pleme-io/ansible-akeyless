#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: encrypt_batch
short_description: Encrypt multiple items in a single batched call
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Encrypt multiple items in a single batched call
options:
    context:
      description: "Encryption context per-line"
      type: dict
    data:
      description: "Base64-encoded plaintext data (per-line)"
      type: str
    item_id:
      description: "Item ID of the key (per-line)"
      type: int
    item_version:
      description: "Key version (per-line)"
      type: int
'''

EXAMPLES = r'''
- name: Run encrypt_batch
  encrypt_batch:
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
    'context': {'type': 'dict'},
    'data': {'type': 'str'},
    'item_id': {'type': 'int'},
    'item_version': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('BatchEncryptionRequestLine', 'encrypt_batch'),
    )


if __name__ == '__main__':
    main()
