#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sra_bastions_info
short_description: List Secure Remote Access bastions
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Retrieve information about sra_bastions_info.
'''

EXAMPLES = r'''
- name: Get sra_bastions_info
  sra_bastions_info:
    register: result
'''

RETURN = r'''
allowed_urls_only:
  description: "Filter the response to show only bastions allowed URLs"
  type: bool
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("ListSRABastions", dict(module.params, token=token))
    return call_api(module, client, "list_sra_bastions", body)


def main():
    argument_spec = {

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
