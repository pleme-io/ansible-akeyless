#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: revoke_certificate
short_description: Revoke a certificate and add it to the CRL
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Revoke a certificate and add it to the CRL
options:
    item_id:
      description: "Item ID of the certificate to revoke"
      type: int
    name:
      description: "Certificate item name"
      type: str
    serial_number:
      description: "Serial number of the certificate"
      type: str
    version:
      description: "Certificate version (required when name/item-id specified)"
      type: int
'''

EXAMPLES = r'''
- name: Run revoke_certificate
  revoke_certificate:
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
    'item_id': {'type': 'int'},
    'name': {'type': 'str'},
    'serial_number': {'type': 'str'},
    'version': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("RevokeCertificate", "revoke_certificate"),
    )


if __name__ == '__main__':
    main()
