#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: item_info
short_description: Describe a specific item (secret, key, or certificate)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Retrieve information about item_info.
options:
    name:
      description: "Item name"
      type: str
'''

EXAMPLES = r'''
- name: Get item_info
  item_info:
    register: result
'''

RETURN = r'''
accessibility:
  description: "for personal password manager"
  type: str
  returned: success
bastion_details:
  description: "Indicate if the item should return with ztb cluster details (url, etc)"
  type: bool
  returned: success
der_certificate_format:
  description: "The certificate will be displayed in DER format"
  type: bool
  returned: success
gateway_details:
  description: "Indicate if the item should return with clusters details (url, etc)"
  type: bool
  returned: success
item_custom_fields_details:
  description: "Include all item custom fields details"
  type: bool
  returned: success
item_id:
  description: "Item id of the item"
  type: int
  returned: success
services_details:
  description: "Include all associated services details"
  type: bool
  returned: success
show_versions:
  description: "Include all item versions in reply"
  type: bool
  returned: success
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_info_module,
)

argument_spec = {
    'name': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_info_module(
        argument_spec=argument_spec,
        sdk_call=('DescribeItem', 'describe_item'),
    )


if __name__ == '__main__':
    main()
