#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_generate_token
short_description: Generate a Universal Identity authentication token
description:
  - Generate a Universal Identity authentication token
options:
    auth_method_name:
      description: "The universal identity auth method name"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Run uid_generate_token
  uid_generate_token:
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
    body = build_body("UidGenerateToken", dict(module.params, token=token))
    return call_api(module, client, "uid_generate_token", body)


def main():
    argument_spec = {
        'auth_method_name': {'type': 'str', 'required': True},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Return token value as-is; playbook author may add no_log: yes
    # to the task to keep it out of the log. Masking here would
    # destroy the value subsequent tasks need.
    module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
