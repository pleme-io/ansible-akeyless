#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_cert
short_description: Manages a certificate authentication method
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage auth_method_cert resources.
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
    allowed_cors:
      description: "Comma separated list of allowed CORS domains to be validated as part of the authentication flow."
      type: str
    audit_logs_claims:
      description: "Subclaims to include in audit logs, e.g '--audit-logs-claims email --audit-logs-claims username'"
      type: list
      elements: str
    bound_common_names:
      description: "Bound common names for certificate matching"
      type: list
      elements: str
    bound_dns_sans:
      description: "Bound DNS SANs for certificate matching"
      type: list
      elements: str
    bound_email_sans:
      description: "Bound email SANs for certificate matching"
      type: list
      elements: str
    bound_extensions:
      description: "Bound extensions (OID:value pairs)"
      type: list
      elements: str
    bound_ips:
      description: "CIDR whitelist for access"
      type: list
      elements: str
    bound_organizational_units:
      description: "Bound organizational units for certificate matching"
      type: list
      elements: str
    bound_uri_sans:
      description: "Bound URI SANs for certificate matching"
      type: list
      elements: str
    certificate_data:
      description: "PEM certificate data for validation"
      type: str
      no_log: true
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
    require_crl_dp:
      description: "Require certificate CRL distribution points (CDP) and enforce CRL validation during authentication."
      type: bool
    revoked_cert_ids:
      description: "Revoked certificate serial numbers"
      type: list
      elements: str
    unique_identifier:
      description: "A unique identifier (ID) value should be configured, such as common_name or organizational_unit
Whenever a user logs in with a token, these authentication types issue
a 'sub claim' that contains details uniquely identifying that user.
This sub claim includes a key containing the ID value that you
configured, and is used to distinguish between different users from
within the same organization."
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create auth_method_cert
  auth_method_cert:
    state: present

- name: Delete auth_method_cert
  auth_method_cert:
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
    'allowed_cors': {'type': 'str'},
    'audit_logs_claims': {'type': 'list', 'elements': 'str'},
    'bound_common_names': {'type': 'list', 'elements': 'str'},
    'bound_dns_sans': {'type': 'list', 'elements': 'str'},
    'bound_email_sans': {'type': 'list', 'elements': 'str'},
    'bound_extensions': {'type': 'list', 'elements': 'str'},
    'bound_ips': {'type': 'list', 'elements': 'str'},
    'bound_organizational_units': {'type': 'list', 'elements': 'str'},
    'bound_uri_sans': {'type': 'list', 'elements': 'str'},
    'certificate_data': {'type': 'str', 'no_log': True},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'force_sub_claims': {'type': 'bool'},
    'gw_bound_ips': {'type': 'list', 'elements': 'str'},
    'jwt_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'product_type': {'type': 'list', 'elements': 'str'},
    'require_crl_dp': {'type': 'bool'},
    'revoked_cert_ids': {'type': 'list', 'elements': 'str'},
    'unique_identifier': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="auth_method_cert",
        sdk_create=("AuthMethodCreateCert", "auth_method_create_cert"),
        sdk_update=("AuthMethodUpdateCert", "auth_method_update_cert"),
        sdk_delete=("DeleteAuthMethod", "delete_auth_method"),
        sdk_read=("GetAuthMethod", "get_auth_method"),
    )


if __name__ == '__main__':
    main()
