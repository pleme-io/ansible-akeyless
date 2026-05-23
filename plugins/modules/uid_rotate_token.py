#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_rotate_token
short_description: Rotate an Akeyless Universal Identity token
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Rotate an Akeyless Universal Identity token
options:
    fork:
      description: "Create a new child token with default parameters"
      type: bool
    send_manual_ack_token:
      description: "Manual ack token for the rotated token"
      type: str
    with_manual_ack:
      description: "Disable automatic ack"
      type: bool
    uid_token:
      description: "Uid token."
      type: str

'''

EXAMPLES = r'''
- name: Run uid_rotate_token
  uid_rotate_token:
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
    body = build_body("UidRotateToken", dict(module.params, token=token))
    return call_api(module, client, "uid_rotate_token", body)


def main():
    argument_spec = {
        'fork': {'type': 'bool'},
        'send_manual_ack_token': {'type': 'str', 'no_log': True},
        'with_manual_ack': {'type': 'bool'},
        # uid_token is the parent token to rotate. Present in the
        # OpenAPI body but iac-forge regen dropped it — stopgap add.
        'uid_token': {'type': 'str', 'no_log': True},
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
