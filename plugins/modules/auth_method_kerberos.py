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


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="auth_method_kerberos created")
    except Exception as e:
        module.fail_json(msg="Failed to create auth_method_kerberos: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="auth_method_kerberos updated")
    except Exception as e:
        module.fail_json(msg="Failed to update auth_method_kerberos: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="auth_method_kerberos deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete auth_method_kerberos: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read auth_method_kerberos: %s" % str(e))


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
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params.get('state', 'present')
    current = read_resource(module)

    if module.check_mode:
        module.exit_json(changed=(current is None and state == 'present')
                         or (current is not None and state == 'absent'))

    if state == 'absent':
        if current is not None:
            delete_resource(module)
        else:
            module.exit_json(changed=False, msg="auth_method_kerberos already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
