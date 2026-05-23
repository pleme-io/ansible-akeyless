#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: classic_key
short_description: Manages a classic cryptographic key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage classic_key resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    alg:
      description: "Classic key algorithm: AES128GCM, AES256GCM, AES128SIV, AES256SIV, RSA1024, RSA2048, RSA3072, RSA4096, EC256, EC384"
      type: str
      required: true
    auto_rotate:
      description: "Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false]"
      type: str
    cert_file_data:
      description: "Certificate PEM data (for RSA keys)"
      type: str
    certificate_common_name:
      description: "Common name for generated certificate"
      type: str
    certificate_country:
      description: "Country for generated certificate"
      type: str
    certificate_digest_algo:
      description: "Digest algorithm to be used for the certificate key signing."
      type: str
    certificate_format:
      description: ""
      type: str
    certificate_locality:
      description: "Locality for generated certificate"
      type: str
    certificate_organization:
      description: "Organization for generated certificate"
      type: str
    certificate_province:
      description: "Province for generated certificate"
      type: str
    certificate_ttl:
      description: "Certificate TTL in days"
      type: int
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Key description"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str
    generate_self_signed_certificate:
      description: "Generate a self-signed certificate"
      type: bool
    gpg_alg:
      description: "gpg alg: Relevant only if GPG key type selected; options: [RSA1024, RSA2048, RSA3072, RSA4096, Ed25519]"
      type: str
    hash_algorithm:
      description: "Specifies the hash algorithm used for the encryption key's operations, available options: [SHA256, SHA384, SHA512]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key_data:
      description: "Key material (base64 encoded)"
      type: str
    name:
      description: "ClassicKey name"
      type: str
      required: true
    protection_key_name:
      description: "Encryption key used to protect this key"
      type: str
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_interval:
      description: "The number of days to wait between every automatic rotation (1-365)"
      type: str
    tags:
      description: "Tags for the key"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create classic_key
  classic_key:
    state: present

- name: Delete classic_key
  classic_key:
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
    'alg': {'type': 'str', 'required': True},
    'auto_rotate': {'type': 'str'},
    'cert_file_data': {'type': 'str', 'no_log': True},
    'certificate_common_name': {'type': 'str'},
    'certificate_country': {'type': 'str'},
    'certificate_digest_algo': {'type': 'str'},
    'certificate_format': {'type': 'str'},
    'certificate_locality': {'type': 'str'},
    'certificate_organization': {'type': 'str'},
    'certificate_province': {'type': 'str'},
    'certificate_ttl': {'type': 'int'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'generate_self_signed_certificate': {'type': 'bool'},
    'gpg_alg': {'type': 'str'},
    'hash_algorithm': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'key_data': {'type': 'str', 'no_log': True},
    'name': {'type': 'str', 'required': True},
    'protection_key_name': {'type': 'str'},
    'rotation_event_in': {'type': 'list', 'elements': 'str'},
    'rotation_interval': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="classic_key",
        sdk_create=("CreateClassicKey", "create_classic_key"),
        sdk_update=("UpdateItem", "update_item"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
