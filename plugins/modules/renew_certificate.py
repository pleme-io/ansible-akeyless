#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: renew_certificate
short_description: Renew an Akeyless PKI certificate
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Renew an Akeyless PKI certificate
options:
    cert_issuer_name:
      description: "Name of the PKI certificate issuer"
      type: str
    generate_key:
      description: "Generate a new key as part of renewal"
      type: bool
    item_id:
      description: "Certificate item ID"
      type: int
    name:
      description: "Certificate name"
      type: str
'''

EXAMPLES = r'''
- name: Run renew_certificate
  renew_certificate:
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
    'cert_issuer_name': {'type': 'str'},
    'generate_key': {'type': 'bool'},
    'item_id': {'type': 'int'},
    'name': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("RenewCertificate", "renew_certificate"),
    )


if __name__ == '__main__':
    main()
