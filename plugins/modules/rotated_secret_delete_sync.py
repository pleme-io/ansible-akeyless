#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_delete_sync
short_description: Delete a rotated-secret sync association
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_action_module,
)

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


def main():
    run_action_module(
        argument_spec=argument_spec,
        sdk_call=('RotatedSecretDeleteSync', 'rotated_secret_delete_sync'),
    )


if __name__ == '__main__':
    main()
