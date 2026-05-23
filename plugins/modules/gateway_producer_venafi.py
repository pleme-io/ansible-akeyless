#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_venafi
short_description: Manages a Venafi gateway producer (deprecated; prefer akeyless_dynamic_secret_venafi)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_venafi resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    admin_rotation_interval_days:
      description: "Admin credentials rotation interval (days)"
      type: int
    allow_subdomains:
      description: "Allow subdomains"
      type: bool
    allowed_domains:
      description: "Allowed domains"
      type: list
      elements: str
    auto_generated_folder:
      description: "Auto generated folder"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    enable_admin_rotation:
      description: "Automatic admin credentials rotation"
      type: bool
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
    root_first_in_chain:
      description: "Root first in chain"
      type: bool
    sign_using_akeyless_pki:
      description: "Use Akeyless PKI issuer or Venafi issuer"
      type: bool
    signer_key_name:
      description: "Signer key name"
      type: str
    store_private_key:
      description: "Store private key"
      type: bool
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL in time.Duration format (2160h / 129600m / etc...). When using sign-using-akeyless-pki certificates created will have this validity period, otherwise the user-ttl is taken from the Validity Period field of the Zone's' Issuing Template. When using cert-manager it is advised to have a TTL of above 60 days (1440h). For more information - https://cert-manager.io/docs/usage/certificate/"
      type: str
    venafi_access_token:
      description: "Venafi Access Token to use to access the TPP environment (Relevant when using TPP)"
      type: str
    venafi_api_key:
      description: "Venafi API key"
      type: str
    venafi_baseurl:
      description: "Venafi Baseurl"
      type: str
    venafi_client_id:
      description: "Venafi Client ID that was used when the access token was generated"
      type: str
    venafi_refresh_token:
      description: "Venafi Refresh Token to use when the Access Token is expired (Relevant when using TPP)"
      type: str
    venafi_use_tpp:
      description: "Venafi using TPP"
      type: bool
    venafi_zone:
      description: "Venafi Zone"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_venafi
  gateway_producer_venafi:
    state: present

- name: Delete gateway_producer_venafi
  gateway_producer_venafi:
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
    'admin_rotation_interval_days': {'type': 'int'},
    'allow_subdomains': {'type': 'bool'},
    'allowed_domains': {'type': 'list', 'elements': 'str'},
    'auto_generated_folder': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'enable_admin_rotation': {'type': 'bool'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'producer_encryption_key_name': {'type': 'str'},
    'root_first_in_chain': {'type': 'bool'},
    'sign_using_akeyless_pki': {'type': 'bool'},
    'signer_key_name': {'type': 'str'},
    'store_private_key': {'type': 'bool'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'venafi_access_token': {'type': 'str'},
    'venafi_api_key': {'type': 'str'},
    'venafi_baseurl': {'type': 'str'},
    'venafi_client_id': {'type': 'str'},
    'venafi_refresh_token': {'type': 'str'},
    'venafi_use_tpp': {'type': 'bool'},
    'venafi_zone': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_producer_venafi",
        sdk_create=("GatewayCreateProducerVenafi", "gateway_create_producer_venafi"),
        sdk_update=("GatewayUpdateProducerVenafi", "gateway_update_producer_venafi"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
