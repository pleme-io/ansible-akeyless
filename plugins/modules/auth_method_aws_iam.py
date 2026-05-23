#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_aws_iam
short_description: Manages an AWS IAM authentication method
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage auth_method_aws_iam resources.
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
    audit_logs_claims:
      description: "Subclaims to include in audit logs, e.g '--audit-logs-claims email --audit-logs-claims username'"
      type: list
      elements: str
    bound_arn:
      description: "Full ARNs to restrict access"
      type: list
      elements: str
    bound_aws_account_id:
      description: "AWS account IDs to restrict access"
      type: list
      required: true
      elements: str
    bound_ips:
      description: "CIDR whitelist for access"
      type: list
      elements: str
    bound_resource_id:
      description: "AWS resource IDs to restrict access"
      type: list
      elements: str
    bound_role_id:
      description: "AWS role IDs to restrict access"
      type: list
      elements: str
    bound_role_name:
      description: "AWS role names to restrict access"
      type: list
      elements: str
    bound_user_id:
      description: "AWS user IDs to restrict access"
      type: list
      elements: str
    bound_user_name:
      description: "AWS user names to restrict access"
      type: list
      elements: str
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
    sts_url:
      description: "STS endpoint URL (default: https://sts.amazonaws.com)"
      type: str
    unique_identifier:
      description: "A unique identifier (ID) value which is a 'sub claim' name that contains details uniquely identifying that resource. This 'sub claim' is used to distinguish between different identities."
      type: str
'''

EXAMPLES = r'''
- name: Create auth_method_aws_iam
  auth_method_aws_iam:
    state: present

- name: Delete auth_method_aws_iam
  auth_method_aws_iam:
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
    'bound_arn': {'type': 'list', 'elements': 'str'},
    'bound_aws_account_id': {'type': 'list', 'required': True, 'elements': 'str'},
    'bound_ips': {'type': 'list', 'elements': 'str'},
    'bound_resource_id': {'type': 'list', 'elements': 'str'},
    'bound_role_id': {'type': 'list', 'elements': 'str'},
    'bound_role_name': {'type': 'list', 'elements': 'str'},
    'bound_user_id': {'type': 'list', 'elements': 'str'},
    'bound_user_name': {'type': 'list', 'elements': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'force_sub_claims': {'type': 'bool'},
    'gw_bound_ips': {'type': 'list', 'elements': 'str'},
    'jwt_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'product_type': {'type': 'list', 'elements': 'str'},
    'sts_url': {'type': 'str'},
    'unique_identifier': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="auth_method_aws_iam",
        sdk_create=("AuthMethodCreateAwsIam", "auth_method_create_aws_iam"),
        sdk_update=("AuthMethodUpdateAwsIam", "auth_method_update_aws_iam"),
        sdk_delete=("DeleteAuthMethod", "delete_auth_method"),
        sdk_read=("GetAuthMethod", "get_auth_method"),
    )


if __name__ == '__main__':
    main()
