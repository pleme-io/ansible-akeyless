#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_create_child_token
short_description: Create a new child token using Akeyless Universal Identity
description:
  - Create a new child token using Akeyless Universal Identity
options:
    auth_method_name:
      description: "The universal identity auth method name (when uid-token is not provided)"
      type: str
    child_deny_inheritance:
      description: "Deny the new child from creating its own children"
      type: bool
    child_deny_rotate:
      description: "Deny the new child from rotating"
      type: bool
    child_ttl:
      description: "TTL of the new child token in seconds"
      type: int
    comment:
      description: "Deprecated - use description"
      type: str
    description:
      description: "Description of the new child"
      type: str
    uid_token_id:
      description: "The ID of the uid-token, required only when uid-token is not provided"
      type: str
'''

EXAMPLES = r'''
- name: Run uid_create_child_token
  uid_create_child_token:
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
    body = build_body("UidCreateChildToken", dict(module.params, token=token))
    return call_api(module, client, "uid_create_child_token", body)


def main():
    argument_spec = {
        'auth_method_name': {'type': 'str'},
        'child_deny_inheritance': {'type': 'bool'},
        'child_deny_rotate': {'type': 'bool'},
        'child_ttl': {'type': 'int'},
        'comment': {'type': 'str'},
        'description': {'type': 'str'},
        'uid_token_id': {'type': 'str'},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    client, token = get_client(module)
    result = run_action(module, client, token)
    # Mask sensitive response fields before echoing back to the user.
    _sensitive = {'token'}
    masked = { k: ('***' if k in _sensitive else v) for k, v in (result or {}).items() }
    module.exit_json(changed=True, result=masked)


if __name__ == '__main__':
    main()
