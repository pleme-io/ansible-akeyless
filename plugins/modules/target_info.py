#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_info
short_description: List targets (use filter to get a specific target)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Retrieve information about target_info.
'''

EXAMPLES = r'''
- name: Get target_info
  target_info:
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
type:
  description: "The target types list . In case it is empty, all
types of targets will be returned. options: [hanadb cassandra aws ssh gke eks mysql mongodb snowflake mssql redshift artifactory azure rabbitmq k8s venafi gcp oracle dockerhub ldap github chef web salesforce postgres]"
  type: list
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("TargetList", dict(module.params, token=token))
    return call_api(module, client, "target_list", body)


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
