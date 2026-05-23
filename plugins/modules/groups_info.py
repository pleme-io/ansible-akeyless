#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: groups_info
short_description: List all groups
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Retrieve information about groups_info.
'''

EXAMPLES = r'''
- name: Get groups_info
  groups_info:
    register: result
'''

RETURN = r'''
filter:
  description: "Filter by auth method name or part of it"
  type: str
  returned: success
pagination_token:
  description: "Next page reference"
  type: str
  returned: success
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_info_module,
)

argument_spec = {

    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_info_module(
        argument_spec=argument_spec,
        sdk_call=('ListGroups', 'list_groups'),
    )


if __name__ == '__main__':
    main()
