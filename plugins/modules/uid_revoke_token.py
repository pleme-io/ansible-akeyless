#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uid_revoke_token
short_description: Revoke a Universal Identity token (self or children)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Revoke a Universal Identity token (self or children)
options:
    auth_method_name:
      description: "The universal identity auth method name"
      type: str
    revoke_token:
      description: "The universal identity token (or token-id) to revoke"
      type: str
      required: true
    revoke_type:
      description: "revokeSelf or revokeAll"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Run uid_revoke_token
  uid_revoke_token:
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
    'revoke_token': {'type': 'str', 'required': True},
    'revoke_type': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=("UidRevokeToken", "uid_revoke_token"),
    )


if __name__ == '__main__':
    main()
