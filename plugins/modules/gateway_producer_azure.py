#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_azure
short_description: Manages an Azure gateway producer (deprecated; prefer akeyless_dynamic_secret_azure)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_producer_azure",
        sdk_create=("GatewayCreateProducerAzure", "gateway_create_producer_azure"),
        sdk_update=("GatewayUpdateProducerAzure", "gateway_update_producer_azure"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
