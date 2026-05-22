#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_azure
short_description: Manages an Azure gateway producer (deprecated; prefer akeyless_dynamic_secret_azure)
description:
  - Manage gateway_producer_azure resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    app_obj_id:
      description: "Azure App Object Id"
      type: str
    azure_administrative_unit:
      description: "Azure AD administrative unit (relevant only when azure-user-portal-access=true)"
      type: str
    azure_client_id:
      description: "Azure Client ID"
      type: str
    azure_client_secret:
      description: "Azure Client Secret"
      type: str
    azure_tenant_id:
      description: "Azure Tenant ID"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "FixedUserClaimKeyname"
      type: str
    fixed_user_only:
      description: "Fixed user"
      type: bool
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    producer_encryption_key_name:
      description: "Dynamic secret encryption key"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_group_obj_id:
      description: "User Group Object Id"
      type: str
    user_portal_access:
      description: "Azure User portal access"
      type: bool
    user_principal_name:
      description: "User Principal Name"
      type: str
    user_programmatic_access:
      description: "Azure User programmatic access"
      type: bool
    user_role_template_id:
      description: "User Role Template Id"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_azure
  gateway_producer_azure:
    state: present

- name: Delete gateway_producer_azure
  gateway_producer_azure:
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
    body = build_body("GatewayCreateProducerAzure", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_azure", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerAzure", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_azure", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'app_obj_id': {'type': 'str'},
        'azure_administrative_unit': {'type': 'str'},
        'azure_client_id': {'type': 'str'},
        'azure_client_secret': {'type': 'str'},
        'azure_tenant_id': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str'},
        'fixed_user_only': {'type': 'bool'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'user_group_obj_id': {'type': 'str'},
        'user_portal_access': {'type': 'bool'},
        'user_principal_name': {'type': 'str'},
        'user_programmatic_access': {'type': 'bool'},
        'user_role_template_id': {'type': 'str'},
        'user_ttl': {'type': 'str'},
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
            module.exit_json(changed=False, msg="gateway_producer_azure already absent")
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
        module.exit_json(changed=False, msg="gateway_producer_azure already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
