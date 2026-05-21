#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: derive_key
short_description: Derive a key from an Akeyless static secret
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("DeriveKey", dict(module.params, token=token))
    return call_api(module, client, "derive_key", body)


def main():
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

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'Key'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
