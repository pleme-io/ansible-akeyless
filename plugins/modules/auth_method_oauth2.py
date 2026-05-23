#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_oauth2
short_description: Manages an OAuth 2.0 authentication method
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage auth_method_oauth2 resources.
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
      description: "OAuth2 audience"
      type: str
    audit_logs_claims:
      description: "Subclaims to include in audit logs, e.g '--audit-logs-claims email --audit-logs-claims username'"
      type: list
      elements: str
    bound_client_ids:
      description: "OAuth2 client IDs to restrict access"
      type: list
      elements: str
    bound_ips:
      description: "CIDR whitelist for access"
      type: list
      elements: str
    cert:
      description: "CertificateFile Path to a file that contain the certificate in a PEM format."
      type: str
    cert_file_data:
      description: "CertificateFileData PEM Certificate in a Base64 format."
      type: str
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
    gateway_url:
      description: "Akeyless Gateway URL (Configuration Management port). Relevant only when the jwks-uri is accessible only from the gateway."
      type: str
    gw_bound_ips:
      description: "Gateway CIDR whitelist"
      type: list
      elements: str
    issuer:
      description: "OAuth2 issuer URL"
      type: str
    jwks_json_data:
      description: "JWKS JSON data for token verification"
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
    subclaims_delimiters:
      description: "A list of additional sub claims delimiters (relevant only for SAML, OIDC, OAuth2/JWT)"
      type: list
      elements: str
    unique_identifier:
      description: "Unique identifier claim name in the JWT token"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create auth_method_oauth2
  auth_method_oauth2:
    state: present

- name: Delete auth_method_oauth2
  auth_method_oauth2:
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
    'bound_client_ids': {'type': 'list', 'elements': 'str'},
    'bound_ips': {'type': 'list', 'elements': 'str'},
    'cert': {'type': 'str'},
    'cert_file_data': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'force_sub_claims': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'gw_bound_ips': {'type': 'list', 'elements': 'str'},
    'issuer': {'type': 'str'},
    'jwks_json_data': {'type': 'str'},
    'jwks_uri': {'type': 'str'},
    'jwt_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'product_type': {'type': 'list', 'elements': 'str'},
    'subclaims_delimiters': {'type': 'list', 'elements': 'str'},
    'unique_identifier': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="auth_method_oauth2",
        sdk_create=("AuthMethodCreateOauth2", "auth_method_create_oauth2"),
        sdk_update=("AuthMethodUpdateOauth2", "auth_method_update_oauth2"),
        sdk_delete=("DeleteAuthMethod", "delete_auth_method"),
        sdk_read=("GetAuthMethod", "get_auth_method"),
    )


if __name__ == '__main__':
    main()
