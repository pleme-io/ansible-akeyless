#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_delete_sync
short_description: Delete a rotated-secret sync association
description:
  - Delete a rotated-secret sync association
options:
    delete_from_usc:
      description: "Also delete the secret from the remote USC"
      type: bool
    name:
      description: "Rotated secret name"
      type: str
      required: true
    remote_secret_name:
      description: "Remote Secret name to disambiguate"
      type: str
    usc_name:
      description: "Universal Secret Connector name"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Run rotated_secret_delete_sync
  rotated_secret_delete_sync:
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
    body = build_body("RotatedSecretDeleteSync", dict(module.params, token=token))
    return call_api(module, client, "rotated_secret_delete_sync", body)


def main():
    argument_spec = {
        'delete_from_usc': {'type': 'bool'},
        'name': {'type': 'str', 'required': True},
        'remote_secret_name': {'type': 'str'},
        'usc_name': {'type': 'str', 'required': True},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = set()
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
