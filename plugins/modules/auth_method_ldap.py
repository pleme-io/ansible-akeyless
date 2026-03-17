#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_ldap
short_description: Manages an LDAP authentication method
description:
  - Manage auth_method_ldap resources.
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
    gen_key:
      description: "Automatically generate a key pair (true/false)"
      type: str
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
    public_key_data:
      description: "A public key generated for LDAP authentication method on Akeyless in base64 or PEM format
[RSA2048]"
      type: str
    unique_identifier:
      description: "A unique identifier (ID) value should be configured for OAuth2,
LDAP and SAML authentication method types and is usually a value such
as the email, username, or upn for example.
Whenever a user logs in with a token, these authentication types issue
a 'sub claim' that contains details uniquely identifying that user.
This sub claim includes a key containing the ID value that you
configured, and is used to distinguish between different users from
within the same organization."
      type: str
'''

EXAMPLES = r'''
- name: Create auth_method_ldap
  auth_method_ldap:
    state: present

- name: Delete auth_method_ldap
  auth_method_ldap:
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
        module.exit_json(changed=True, msg="auth_method_ldap created")
    except Exception as e:
        module.fail_json(msg="Failed to create auth_method_ldap: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="auth_method_ldap updated")
    except Exception as e:
        module.fail_json(msg="Failed to update auth_method_ldap: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="auth_method_ldap deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete auth_method_ldap: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read auth_method_ldap: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'access_expires': {'type': 'int'},
        'allowed_client_type': {'type': 'list', 'elements': 'str'},
        'audit_logs_claims': {'type': 'list', 'elements': 'str'},
        'bound_ips': {'type': 'list', 'elements': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'force_sub_claims': {'type': 'bool'},
        'gen_key': {'type': 'str'},
        'gw_bound_ips': {'type': 'list', 'elements': 'str'},
        'jwt_ttl': {'type': 'int'},
        'name': {'type': 'str', 'required': True},
        'product_type': {'type': 'list', 'elements': 'str'},
        'public_key_data': {'type': 'str'},
        'unique_identifier': {'type': 'str'},
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
            module.exit_json(changed=False, msg="auth_method_ldap already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
