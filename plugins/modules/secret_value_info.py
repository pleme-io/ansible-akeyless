#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: secret_value_info
short_description: Read the value of a static secret
description:
  - Retrieve information about secret_value_info.
options:
    names:
      description: "Secret name"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Get secret_value_info
  secret_value_info:
    register: result
'''

RETURN = r'''
accessibility:
  description: "for personal password manager"
  type: str
  returned: success
ignore_cache:
  description: "Retrieve the Secret value without checking the Gateway's cache [true/false]. This flag is only relevant when using the RestAPI"
  type: str
  returned: success
pretty_print:
  description: "Print the secret value with json-pretty-print (not relevent to SDK)"
  type: bool
  returned: success
version:
  description: "Secret version, if negative value N is provided the last N versions will return (maximum 20)"
  type: int
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("GetSecretValue", dict(module.params, token=token))
    return call_api(module, client, "get_secret_value", body)


def main():
    argument_spec = {
        'names': {'type': 'list', 'elements': 'str'},
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
