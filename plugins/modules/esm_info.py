#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: esm_info
short_description: List external secrets manager integrations
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Retrieve information about esm_info.
options:

    esm_name:
      description: "Name of the External Secrets Manager item"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Get esm_info
  esm_info:
    register: result
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("EsmList", dict(module.params, token=token))
    return call_api(module, client, "esm_list", body)


def main():
    argument_spec = {
        'esm_name': {'required': True, 'type': 'str'},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        'access_key': {'type': 'str', 'no_log': True},
        'access_type': {'type': 'str', 'default': 'access_key'},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    result = read_resource(module, client, token) or {}
    module.exit_json(changed=False, result=result)


if __name__ == '__main__':
    main()
