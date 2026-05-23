#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_cert_challenge
short_description: Get a challenge for certificate-based authentication
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Get a challenge for certificate-based authentication
options:
    access_id:
      description: "Access ID for the cert auth method"
      type: str
    cert_data:
      description: "Base64-encoded certificate data"
      type: str
'''

EXAMPLES = r'''
- name: Run get_cert_challenge
  get_cert_challenge:
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
    'access_id': {'type': 'str'},
    'cert_data': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("GetCertChallenge", "get_cert_challenge"),
    )


if __name__ == '__main__':
    main()
