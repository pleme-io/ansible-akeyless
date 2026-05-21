#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_list_children
short_description: List child token IDs of an Akeyless Universal Identity
description:
  - List child token IDs of an Akeyless Universal Identity
options:
    auth_method_name:
      description: "The universal identity auth method name (when uid-token is not provided)"
      type: str
'''

EXAMPLES = r'''
- name: Run uid_list_children
  uid_list_children:
  register: result
'''

RETURN = r'''
result:
  description: "Raw result of the action call"
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def run_action(module, client, token):
    """Invoke the action and return the SDK response."""
    body = build_body("UidListChildren", dict(module.params, token=token))
    return call_api(module, client, "uid_list_children", body)


def main():
    argument_spec = {
        'auth_method_name': {'type': 'str'},
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
    module.exit_json(changed=False, result=masked)


if __name__ == '__main__':
    main()
