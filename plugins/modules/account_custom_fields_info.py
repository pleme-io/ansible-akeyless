#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: account_custom_fields_info
short_description: List account custom fields
description:
  - Retrieve information about account_custom_fields_info.
options:

'''

EXAMPLES = r'''
- name: Get account_custom_fields_info
  account_custom_fields_info:
    register: result
'''

RETURN = r'''
object:
  description: "The object to filter by the custom fields
in: body"
  type: str
  returned: success
object_type:
  description: "The object type to filter by the custom fields
in: body"
  type: str
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("AccountCustomFieldList", dict(module.params, token=token))
    return call_api(module, client, "account_custom_field_list", body)


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
