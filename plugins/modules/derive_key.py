#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: derive_key
short_description: Derive a key from an Akeyless static secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Derive a key from an Akeyless static secret
options:
    accessibility:
      description: "Item accessibility (default: regular)"
      type: str
    alg:
      description: "KDF algorithm (default: pbkdf2)"
      type: str
      required: true
    hash_function:
      description: "Hash function (pbkdf2 only)"
      type: str
    iter:
      description: "Iteration count"
      type: int
      required: true
    key_len:
      description: "Derived key length in bytes"
      type: int
      required: true
    mem:
      description: "Memory size in kB (argon2id only)"
      type: int
    name:
      description: "Static secret full name"
      type: str
      required: true
    parallelism:
      description: "Parallelism (argon2id only)"
      type: int
    salt:
      description: "Base64-encoded salt (auto-generated if absent)"
      type: str
'''

EXAMPLES = r'''
- name: Run derive_key
  derive_key:
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
    'accessibility': {'type': 'str'},
    'alg': {'type': 'str', 'required': True},
    'hash_function': {'type': 'str'},
    'iter': {'type': 'int', 'required': True},
    'key_len': {'type': 'int', 'required': True},
    'mem': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'parallelism': {'type': 'int'},
    'salt': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("DeriveKey", "derive_key"),
    )


if __name__ == '__main__':
    main()
