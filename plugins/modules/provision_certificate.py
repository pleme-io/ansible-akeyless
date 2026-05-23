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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("ProvisionCertificate", dict(module.params, token=token))
    return call_api(module, client, "provision_certificate", body)


def main():
    argument_spec = {
        'display_id': {'type': 'str'},
        'item_id': {'type': 'int'},
        'name': {'type': 'str', 'required': True},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'certificate', 'private_key'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
