#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: generate_csr
short_description: Generate a Certificate Signing Request
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Generate a Certificate Signing Request
options:
    alg:
      description: "Classic key algorithm"
      type: str
    alt_names:
      description: "Comma-separated DNS alt names"
      type: str
    certificate_type:
      description: "Certificate type (ssl-client / ssl-server / certificate-signing)"
      type: str
    city:
      description: "City for the CSR subject"
      type: str
    common_name:
      description: "Common name for the CSR"
      type: str
      required: true
    country:
      description: "Country for the CSR subject"
      type: str
    critical:
      description: "Mark key usage as critical"
      type: bool
    dep:
      description: "Department for the CSR subject"
      type: str
    email_addresses:
      description: "Comma-separated email alt names"
      type: str
    export_private_key:
      description: "Whether to export the private key"
      type: bool
    generate_key:
      description: "Generate a new classic key for the CSR"
      type: bool
    hash_algorithm:
      description: "Hash algorithm (SHA256/384/512)"
      type: str
    ip_addresses:
      description: "Comma-separated IP alt names"
      type: str
    key_type:
      description: "Key type (classic-key or dfc)"
      type: str
      required: true
    name:
      description: "Key name"
      type: str
      required: true
    org:
      description: "Organization for the CSR subject"
      type: str
    split_level:
      description: "Number of secret fragments"
      type: int
    state:
      description: "State for the CSR subject"
      type: str
    uri_sans:
      description: "Comma-separated URI alt names"
      type: str
'''

EXAMPLES = r'''
- name: Run generate_csr
  generate_csr:
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
    'alt_names': {'type': 'str'},
    'certificate_type': {'type': 'str'},
    'city': {'type': 'str'},
    'common_name': {'type': 'str', 'required': True},
    'country': {'type': 'str'},
    'critical': {'type': 'bool'},
    'dep': {'type': 'str'},
    'email_addresses': {'type': 'str'},
    'export_private_key': {'type': 'bool'},
    'generate_key': {'type': 'bool'},
    'hash_algorithm': {'type': 'str'},
    'ip_addresses': {'type': 'str'},
    'key_type': {'type': 'str', 'required': True},
    'name': {'type': 'str', 'required': True},
    'org': {'type': 'str'},
    'split_level': {'type': 'int'},
    'state': {'type': 'str'},
    'uri_sans': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('GenerateCsr', 'generate_csr'),
    )


if __name__ == '__main__':
    main()
