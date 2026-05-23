#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_azure_ad
short_description: Manages an Azure AD authentication method
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage auth_method_azure_ad resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_expires:
      description: "Access expiration in Unix time (0 = no expiry)"
      type: int
    allowed_client_type:
      description: "limit the auth method usage for specific client types [cli,ui,gateway-admin,sdk,mobile,extension]"
      type: list
      elements: str
    audience:
      description: "Azure AD audience (application ID)"
      type: str
    audit_logs_claims:
      description: "Subclaims to include in audit logs, e.g '--audit-logs-claims email --audit-logs-claims username'"
      type: list
      elements: str
    bound_group_id:
      description: "Azure AD group IDs to restrict access"
      type: list
      elements: str
    bound_ips:
      description: "CIDR whitelist for access"
      type: list
      elements: str
    bound_providers:
      description: "Azure resource providers to restrict access"
      type: list
      elements: str
    bound_resource_id:
      description: "Azure resource IDs to restrict access"
      type: list
      elements: str
    bound_resource_names:
      description: "Azure resource names to restrict access"
      type: list
      elements: str
    bound_resource_types:
      description: "Azure resource types to restrict access"
      type: list
      elements: str
    bound_rg_id:
      description: "Azure resource group IDs to restrict access"
      type: list
      elements: str
    bound_spid:
      description: "Service principal IDs to restrict access"
      type: list
      elements: str
    bound_sub_id:
      description: "Azure subscription IDs to restrict access"
      type: list
      elements: str
    bound_tenant_id:
      description: "Azure tenant ID to restrict access"
      type: str
      required: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Auth Method description"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the auth method would you like to be notified."
      type: list
      elements: str
    force_sub_claims:
      description: "Force sub-claims enforcement"
      type: bool
    gw_bound_ips:
      description: "Gateway CIDR whitelist"
      type: list
      elements: str
    issuer:
      description: "Azure AD issuer URL"
      type: str
    jwks_uri:
      description: "JWKS URI for token verification"
      type: str
    jwt_ttl:
      description: "JWT TTL in seconds"
      type: int
    name:
      description: "Auth Method name"
      type: str
      required: true
    product_type:
      description: "Choose the relevant product type for the auth method [sm, sra, pm, dp, ca]"
      type: list
      elements: str
    unique_identifier:
      description: "A unique identifier (ID) value which is a 'sub claim' name that contains details uniquely identifying that resource. This 'sub claim' is used to distinguish between different identities."
      type: str
'''

EXAMPLES = r'''
- name: Create auth_method_azure_ad
  auth_method_azure_ad:
    state: present

- name: Delete auth_method_azure_ad
  auth_method_azure_ad:
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
    'audience': {'type': 'str'},
    'audit_logs_claims': {'type': 'list', 'elements': 'str'},
    'bound_group_id': {'type': 'list', 'elements': 'str'},
    'bound_ips': {'type': 'list', 'elements': 'str'},
    'bound_providers': {'type': 'list', 'elements': 'str'},
    'bound_resource_id': {'type': 'list', 'elements': 'str'},
    'bound_resource_names': {'type': 'list', 'elements': 'str'},
    'bound_resource_types': {'type': 'list', 'elements': 'str'},
    'bound_rg_id': {'type': 'list', 'elements': 'str'},
    'bound_spid': {'type': 'list', 'elements': 'str'},
    'bound_sub_id': {'type': 'list', 'elements': 'str'},
    'bound_tenant_id': {'type': 'str', 'required': True},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'force_sub_claims': {'type': 'bool'},
    'gw_bound_ips': {'type': 'list', 'elements': 'str'},
    'issuer': {'type': 'str'},
    'jwks_uri': {'type': 'str'},
    'jwt_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'product_type': {'type': 'list', 'elements': 'str'},
    'unique_identifier': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="auth_method_azure_ad",
        sdk_create=("AuthMethodCreateAzureAD", "auth_method_create_azure_ad"),
        sdk_update=("AuthMethodUpdateAzureAD", "auth_method_update_azure_ad"),
        sdk_delete=("DeleteAuthMethod", "delete_auth_method"),
        sdk_read=("GetAuthMethod", "get_auth_method"),
    )


if __name__ == '__main__':
    main()
