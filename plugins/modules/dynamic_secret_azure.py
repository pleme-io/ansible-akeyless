#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_azure
short_description: Manages an Azure dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_azure resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    app_obj_id:
      description: "Azure application object ID"
      type: str
    azure_administrative_unit:
      description: "Azure AD administrative unit (relevant only when azure-user-portal-access=true)"
      type: str
    azure_client_id:
      description: "Azure client/application ID"
      type: str
    azure_client_secret:
      description: "Azure client secret"
      type: str
    azure_tenant_id:
      description: "Azure tenant ID"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
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
      description: "Dynamic producer encryption key"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    user_group_obj_id:
      description: "Azure user group object ID"
      type: str
    user_portal_access:
      description: "Enable Azure portal access"
      type: bool
    user_principal_name:
      description: "User Principal Name"
      type: str
    user_programmatic_access:
      description: "Enable Azure programmatic access"
      type: bool
    user_role_template_id:
      description: "Azure role template ID"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_azure
  dynamic_secret_azure:
    state: present

- name: Delete dynamic_secret_azure
  dynamic_secret_azure:
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
    body = build_body("DynamicSecretCreateAzure", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_create_azure", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("DynamicSecretUpdateAzure", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_update_azure", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DynamicSecretDelete", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DynamicSecretGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "dynamic_secret_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'app_obj_id': {'type': 'str'},
        'azure_administrative_unit': {'type': 'str'},
        'azure_client_id': {'type': 'str'},
        'azure_client_secret': {'type': 'str', 'no_log': True},
        'azure_tenant_id': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str', 'no_log': False},
        'fixed_user_only': {'type': 'bool'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str', 'no_log': False},
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
            module.exit_json(changed=False, msg="dynamic_secret_azure already absent")
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
        module.exit_json(changed=False, msg="dynamic_secret_azure already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
