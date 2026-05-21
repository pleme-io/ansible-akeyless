#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: renew_certificate
short_description: Renew an Akeyless PKI certificate
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("RenewCertificate", dict(module.params, token=token))
    return call_api(module, client, "renew_certificate", body)


def main():
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

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'cert', 'private_key', 'reading_token'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
