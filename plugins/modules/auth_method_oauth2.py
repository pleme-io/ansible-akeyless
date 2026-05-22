#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_oauth2
short_description: Manages an OAuth 2.0 authentication method
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("AuthMethodCreateOauth2", dict(module.params, token=token))
    return call_api(module, client, "auth_method_create_oauth2", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("AuthMethodUpdateOauth2", dict(module.params, token=token))
    return call_api(module, client, "auth_method_update_oauth2", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteAuthMethod", dict(module.params, token=token))
    return call_api(module, client, "delete_auth_method", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GetAuthMethod", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "get_auth_method", body, swallow_404=True)


def main():
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="auth_method_oauth2 already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        result = delete_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # state == 'present'
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = create_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs
    # from what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False, msg="auth_method_oauth2 already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
