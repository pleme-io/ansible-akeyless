#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: secret_value_info
short_description: Read the value of a static secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_info_module,
)

argument_spec = {
    'names': {'type': 'list', 'elements': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_info_module(
        argument_spec=argument_spec,
        sdk_call=("GetSecretValue", "get_secret_value"),
    )


if __name__ == '__main__':
    main()
