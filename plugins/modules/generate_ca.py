#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: generate_ca
short_description: Create a new PKI CA + intermediate issuer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Create a new PKI CA + intermediate issuer
options:
    alg:
      description: "Classic key algorithm"
      type: str
    allowed_domains:
      description: "Comma-delimited list of allowed domains"
      type: str
      required: true
    delete_protection:
      description: "Delete-protection flag (true/false string)"
      type: str
    extended_key_usage:
      description: "Extended key usage (default: serverauth,clientauth)"
      type: str
    key_type:
      description: "Key type"
      type: str
    max_path_len:
      description: "Maximum intermediate cert path length"
      type: int
    pki_chain_name:
      description: "PKI chain name"
      type: str
      required: true
    protection_key_name:
      description: "Protection key (default account key if empty)"
      type: str
    split_level:
      description: "Number of secret fragments"
      type: int
    ttl:
      description: "Maximum TTL for issued certificates (s/m/h/d)"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Run generate_ca
  generate_ca:
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
    'alg': {'type': 'str'},
    'allowed_domains': {'type': 'str', 'required': True},
    'delete_protection': {'type': 'str'},
    'extended_key_usage': {'type': 'str'},
    'key_type': {'type': 'str'},
    'max_path_len': {'type': 'int'},
    'pki_chain_name': {'type': 'str', 'required': True},
    'protection_key_name': {'type': 'str'},
    'split_level': {'type': 'int'},
    'ttl': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('GenerateCA', 'generate_ca'),
    )


if __name__ == '__main__':
    main()
