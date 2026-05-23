#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_create_child_token
short_description: Create a new child token using Akeyless Universal Identity
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_action_module,
)

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


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('UidCreateChildToken', 'uid_create_child_token'),
    )


if __name__ == '__main__':
    main()
