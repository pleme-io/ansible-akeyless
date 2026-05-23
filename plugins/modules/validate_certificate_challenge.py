#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: validate_certificate_challenge
short_description: Validate HTTP-01 challenge and finalize certificate issuance
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Validate HTTP-01 challenge and finalize certificate issuance
options:
    Result:
      description: ""
      type: dict
    cert_display_id:
      description: "Certificate display ID from Phase 1"
      type: str
    name:
      description: "Certificate name (alternative to cert-display-id)"
      type: str
    timeout:
      description: "Validation timeout in seconds (default: 120)"
      type: int
'''

EXAMPLES = r'''
- name: Run validate_certificate_challenge
  validate_certificate_challenge:
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
    'Result': {'type': 'dict'},
    'cert_display_id': {'type': 'str'},
    'name': {'type': 'str'},
    'timeout': {'type': 'int'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('ValidateCertificateChallenge', 'validate_certificate_challenge'),
    )


if __name__ == '__main__':
    main()
