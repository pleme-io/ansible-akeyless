#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_kerberos
short_description: Manages a Kerberos authentication method
description:
  - Manage auth_method_kerberos resources.
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
    bind_dn:
      description: ""
      type: str
    bind_dn_password:
      description: ""
      type: str
    bound_ips:
      description: "CIDR whitelist for access"
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
    group_attr:
      description: ""
      type: str
    group_dn:
      description: ""
      type: str
    group_filter:
      description: ""
      type: str
    gw_bound_ips:
      description: "Gateway CIDR whitelist"
      type: list
      elements: str
    jwt_ttl:
      description: "JWT TTL in seconds"
      type: int
    keytab_file_data:
      description: "Kerberos keytab file data (base64)"
      type: str
      no_log: true
    keytab_file_path:
      description: "Path to Kerberos keytab file on gateway"
      type: str
    krb5_conf_data:
      description: "Kerberos krb5.conf file data (base64)"
      type: str
    krb5_conf_path:
      description: "Path to krb5.conf file on gateway"
      type: str
    ldap_anonymous_search:
      description: ""
      type: bool
    ldap_ca_cert:
      description: ""
      type: str
    ldap_url:
      description: ""
      type: str
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
      description: "A unique identifier (ID) value which is a 'sub claim' name that contains details uniquely identifying that resource. This 'sub claim' is used to distinguish between different identities."
      type: str
    user_attribute:
      description: ""
      type: str
    user_dn:
      description: ""
      type: str
'''

EXAMPLES = r'''
- name: Create auth_method_kerberos
  auth_method_kerberos:
    state: present

- name: Delete auth_method_kerberos
  auth_method_kerberos:
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
    body = build_body("AuthMethodCreateKerberos", dict(module.params, token=token))
    return call_api(module, client, "auth_method_create_kerberos", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("AuthMethodUpdateKerberos", dict(module.params, token=token))
    return call_api(module, client, "auth_method_update_kerberos", body)


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
        'audit_logs_claims': {'type': 'list', 'elements': 'str'},
        'bind_dn': {'type': 'str'},
        'bind_dn_password': {'type': 'str'},
        'bound_ips': {'type': 'list', 'elements': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'force_sub_claims': {'type': 'bool'},
        'group_attr': {'type': 'str'},
        'group_dn': {'type': 'str'},
        'group_filter': {'type': 'str'},
        'gw_bound_ips': {'type': 'list', 'elements': 'str'},
        'jwt_ttl': {'type': 'int'},
        'keytab_file_data': {'type': 'str', 'no_log': True},
        'keytab_file_path': {'type': 'str'},
        'krb5_conf_data': {'type': 'str'},
        'krb5_conf_path': {'type': 'str'},
        'ldap_anonymous_search': {'type': 'bool'},
        'ldap_ca_cert': {'type': 'str'},
        'ldap_url': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'product_type': {'type': 'list', 'elements': 'str'},
        'subclaims_delimiters': {'type': 'list', 'elements': 'str'},
        'unique_identifier': {'type': 'str'},
        'user_attribute': {'type': 'str'},
        'user_dn': {'type': 'str'},
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
            module.exit_json(changed=False, msg="auth_method_kerberos already absent")
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
        module.exit_json(changed=False, msg="auth_method_kerberos already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
