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
        sdk_call=('ListSRABastions', 'list_sra_bastions'),
    )


if __name__ == '__main__':
    main()
