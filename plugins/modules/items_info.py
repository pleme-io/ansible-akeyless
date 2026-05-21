#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: items_info
short_description: List all items (secrets, keys, certificates)
description:
  - Retrieve information about items_info.
options:

'''

EXAMPLES = r'''
- name: Get items_info
  items_info:
    register: result
'''

RETURN = r'''
accessibility:
  description: "for personal password manager"
  type: str
  returned: success
advanced_filter:
  description: "Filter by item name/username/website or part of it"
  type: str
  returned: success
auto_pagination:
  description: "Retrieve all items using pagination, when disabled retrieving only first 1000 items"
  type: str
  returned: success
current_folder:
  description: "List only items in the current folder (excludes subfolders)"
  type: bool
  returned: success
filter:
  description: "Filter by item name or part of it"
  type: str
  returned: success
minimal_view:
  description: "Show only basic information of the items"
  type: bool
  returned: success
modified_after:
  description: "List only secrets modified after specified date (in unix time)"
  type: int
  returned: success
pagination_token:
  description: "Next page reference"
  type: str
  returned: success
path:
  description: "Path to folder"
  type: str
  returned: success
sra_only:
  description: "Filter by items with SRA functionality enabled"
  type: bool
  returned: success
sub_types:
  description: ""
  type: list
  returned: success
tag:
  description: "Filter by item tag"
  type: str
  returned: success
type:
  description: "The item types list of the requested items. In case it is empty, all
types of items will be returned. options: [key, static-secret,
dynamic-secret, classic-key]"
  type: list
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("ListItems", dict(module.params, token=token))
    return call_api(module, client, "list_items", body)


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
