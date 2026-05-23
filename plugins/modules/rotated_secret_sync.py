#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_sync
short_description: Sync a rotated secret value to a Universal Secret Connector
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Sync a rotated secret value to a Universal Secret Connector
options:
    DeleteRemote:
      description: "Delete the secret from the remote manager on update"
      type: bool
    filter_secret_value:
      description: "JQ expression to filter / transform the secret value"
      type: str
    name:
      description: "Rotated secret name"
      type: str
      required: true
    namespace:
      description: "Vault namespace (Hashicorp Vault targets only)"
      type: str
    remote_secret_name:
      description: "Remote secret name on the USC side"
      type: str
    usc_name:
      description: "Universal Secret Connector name (if absent, all attached USCs are synced)"
      type: str
'''

EXAMPLES = r'''
- name: Run rotated_secret_sync
  rotated_secret_sync:
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
    body = build_body("RotatedSecretSync", dict(module.params, token=token))
    return call_api(module, client, "rotated_secret_sync", body)


def main():
    argument_spec = {
        'DeleteRemote': {'type': 'bool'},
        'filter_secret_value': {'type': 'str', 'no_log': False},
        'name': {'type': 'str', 'required': True},
        'namespace': {'type': 'str'},
        'remote_secret_name': {'type': 'str'},
        'usc_name': {'type': 'str'},
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
