#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_gcp
short_description: Manages a GCP gateway producer (deprecated; prefer akeyless_dynamic_secret_gcp)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_gcp resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_type:
      description: ""
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (Relevant only when --access-type=external)"
      type: str
    gcp_cred_type:
      description: ""
      type: str
    gcp_key:
      description: "Base64-encoded service account private key text"
      type: str
    gcp_key_algo:
      description: "Service account key algorithm, e.g. KEY_ALG_RSA_1024 (Relevant only when --access-type=sa and --gcp-cred-type=key)"
      type: str
    gcp_project_id:
      description: "GCP Project ID override for dynamic secret operations"
      type: str
    gcp_sa_email:
      description: "The email of the fixed service account to generate keys or tokens for (Relevant only when --access-type=sa and --service-account-type=fixed)"
      type: str
    gcp_token_scopes:
      description: "Access token scopes list, e.g. scope1,scope2 (Relevant only when --access-type=sa; required when --gcp-cred-type=token)"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    role_binding:
      description: "Role binding definitions in JSON format (Relevant only when --access-type=sa and --service-account-type=dynamic)"
      type: str
    role_names:
      description: "Comma-separated list of GCP roles to assign to the user (Relevant only when --access-type=external)"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    service_account_type:
      description: "The type of the GCP service account. Options [fixed, dynamic] (Relevant only when --access-type=sa)"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_gcp
  gateway_producer_gcp:
    state: present

- name: Delete gateway_producer_gcp
  gateway_producer_gcp:
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
    'access_type': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'fixed_user_claim_keyname': {'type': 'str', 'no_log': False},
    'gcp_cred_type': {'type': 'str'},
    'gcp_key': {'type': 'str', 'no_log': True},
    'gcp_key_algo': {'type': 'str', 'no_log': False},
    'gcp_project_id': {'type': 'str'},
    'gcp_sa_email': {'type': 'str'},
    'gcp_token_scopes': {'type': 'str', 'no_log': False},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'producer_encryption_key_name': {'type': 'str'},
    'role_binding': {'type': 'str'},
    'role_names': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'service_account_type': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='gateway_producer_gcp',
        sdk_create=('GatewayCreateProducerGcp', 'gateway_create_producer_gcp'),
        sdk_update=('GatewayUpdateProducerGcp', 'gateway_update_producer_gcp'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
