#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: provision_certificate
short_description: Provision an Akeyless certificate to a target
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Provision an Akeyless certificate to a target
options:
    display_id:
      description: "Certificate display ID"
      type: str
    item_id:
      description: "Certificate item ID"
      type: int
    name:
      description: "Certificate name"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Run provision_certificate
  provision_certificate:
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
    'display_id': {'type': 'str'},
    'item_id': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('ProvisionCertificate', 'provision_certificate'),
    )


if __name__ == '__main__':
    main()
