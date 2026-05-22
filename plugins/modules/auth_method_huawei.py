#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_method_huawei
short_description: Manages a Huawei authentication method in Akeyless Vault
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("CreateAuthMethodHuawei", dict(module.params, token=token))
    return call_api(module, client, "create_auth_method_huawei", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdateAuthMethod", dict(module.params, token=token))
    return call_api(module, client, "update_auth_method", body)


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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="auth_method_huawei already absent")
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
        module.exit_json(changed=False, msg="auth_method_huawei already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
