#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_huawei
short_description: Manages a Huawei authentication method in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage auth_method_huawei resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present

    access_expires:
      description: "Access expiration date in Unix timestamp (select 0 for access without
      type: int
expiry date)"
      type: int
    allowed_client_type:
      description: "limit the auth method usage for specific client types [cli,ui,gateway-admin,sdk,mobile,extension]"
      type: list
      elements: str
    audit_logs_claims:
      description: "Subclaims to include in audit logs, e.g '--audit-logs-claims email --audit-logs-claims username'"
      type: list
      elements: str
    auth_url:
      description: "sts URL"
      type: str
    bound_domain_id:
      description: "A list of domain IDs that the access is restricted to"
      type: list
      elements: str
    bound_domain_name:
      description: "A list of domain names that the access is restricted to"
      type: list
      elements: str
    bound_ips:
      description: "A CIDR whitelist with the IPs that the access is restricted to"
      type: list
      elements: str
    bound_tenant_id:
      description: "A list of full tenant ids that the access is restricted to"
      type: list
      elements: str
    bound_tenant_name:
      description: "A list of full tenant names that the access is restricted to"
      type: list
      elements: str
    bound_user_id:
      description: "A list of full user ids that the access is restricted to"
      type: list
      elements: str
    bound_user_name:
      description: "A list of full user-name that the access is restricted to"
      type: list
      elements: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Auth Method description"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the auth method would you like to be notified."
      type: list
      elements: str
    force_sub_claims:
      description: "if true: enforce role-association must include sub claims"
      type: bool
    gw_bound_ips:
      description: "A CIDR whitelist with the GW IPs that the access is restricted to"
      type: list
      elements: str
    jwt_ttl:
      description: "Jwt TTL"
      type: int
    name:
      description: "Auth Method name"
      type: str
      required: true
    product_type:
      description: "Choose the relevant product type for the auth method [sm, sra, pm, dp, ca]"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create auth_method_huawei
  auth_method_huawei:
    state: present

- name: Delete auth_method_huawei
  auth_method_huawei:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

argument_spec = {
    'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
    'access_expires': {'type': 'int'},
    'allowed_client_type': {'type': 'list', 'elements': 'str'},
    'audit_logs_claims': {'type': 'list', 'elements': 'str'},
    'auth_url': {'type': 'str'},
    'bound_domain_id': {'type': 'list', 'elements': 'str'},
    'bound_domain_name': {'type': 'list', 'elements': 'str'},
    'bound_ips': {'type': 'list', 'elements': 'str'},
    'bound_tenant_id': {'type': 'list', 'elements': 'str'},
    'bound_tenant_name': {'type': 'list', 'elements': 'str'},
    'bound_user_id': {'type': 'list', 'elements': 'str'},
    'bound_user_name': {'type': 'list', 'elements': 'str'},
    'delete_protection': {'type': 'str'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'force_sub_claims': {'type': 'bool'},
    'gw_bound_ips': {'type': 'list', 'elements': 'str'},
    'jwt_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'product_type': {'type': 'list', 'elements': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='auth_method_huawei',
        sdk_create=('CreateAuthMethodHuawei', 'create_auth_method_huawei'),
        sdk_update=('UpdateAuthMethod', 'update_auth_method'),
        sdk_delete=('DeleteAuthMethod', 'delete_auth_method'),
        sdk_read=('GetAuthMethod', 'get_auth_method'),
    )


if __name__ == '__main__':
    main()
