#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_methods_info
short_description: List all authentication methods
description:
  - Retrieve information about auth_methods_info.
options:

'''

EXAMPLES = r'''
- name: Get auth_methods_info
  auth_methods_info:
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
  description: "The Auth method types list of the requested method. In case it is empty, all
types of auth methods will be returned. options: [api_key, azure_ad, oauth2/jwt, saml2,
ldap, aws_iam, oidc, universal_identity, gcp, k8s, cert]"
  type: list
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def read_resource(module, client, token):
    """Read the data source."""
    body = build_body("ListAuthMethods", dict(module.params, token=token))
    return call_api(module, client, "list_auth_methods", body)


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
