#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_ldap
short_description: Manages an LDAP dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_ldap resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    ProviderType:
      description: ""
      type: str
    bind_dn:
      description: "LDAP bind DN"
      type: str
    bind_dn_password:
      description: "LDAP bind DN password"
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
    external_username:
      description: "External username for fixed mode"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (relevant only for external-username=true)"
      type: str
    group_dn:
      description: "Group DN for dynamic users"
      type: str
    host_provider:
      description: "Host provider type [explicit/target], Default Host provider is explicit, Relevant only for Secure Remote Access of ssh cert issuer, ldap rotated secret and ldap dynamic secret"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    ldap_ca_cert:
      description: "CA Certificate File Content"
      type: str
    ldap_url:
      description: "LDAP server URL"
      type: str
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
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    secure_access_rd_gateway_server:
      description: "RD Gateway server"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target:
      description: "A list of linked targets to be associated, Relevant only for Secure Remote Access for ssh cert issuer, ldap rotated secret and ldap dynamic secret, To specify multiple targets use argument multiple times"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    token_expiration:
      description: "LDAP token expiration in seconds"
      type: str
    user_attribute:
      description: "LDAP user attribute"
      type: str
    user_dn:
      description: "Base DN for user creation"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_ldap
  dynamic_secret_ldap:
    state: present

- name: Delete dynamic_secret_ldap
  dynamic_secret_ldap:
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
    'ProviderType': {'type': 'str'},
    'bind_dn': {'type': 'str'},
    'bind_dn_password': {'type': 'str', 'no_log': True},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'external_username': {'type': 'str'},
    'fixed_user_claim_keyname': {'type': 'str'},
    'group_dn': {'type': 'str'},
    'host_provider': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'ldap_ca_cert': {'type': 'str'},
    'ldap_url': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'secure_access_rd_gateway_server': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'token_expiration': {'type': 'str'},
    'user_attribute': {'type': 'str'},
    'user_dn': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_ldap",
        sdk_create=("DynamicSecretCreateLdap", "dynamic_secret_create_ldap"),
        sdk_update=("DynamicSecretUpdateLdap", "dynamic_secret_update_ldap"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
