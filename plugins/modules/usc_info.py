#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: usc_info
short_description: List universal secrets connectors
description:
  - Retrieve information about usc_info.
options:
    usc_name:
      description: "Name of the Universal Secrets Connector item"
      type: str
'''

EXAMPLES = r'''
- name: Get usc_info
  usc_info:
    register: result
'''

RETURN = r'''
object_type:
  description: ""
  type: str
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("UscList", dict(module.params, token=token))
    return call_api(module, client, "usc_list", body)


def main():
    argument_spec = {
        'usc_name': {'type': 'str'},
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
