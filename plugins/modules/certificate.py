#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: certificate
short_description: Manages a certificate in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage certificate resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_data:
      description: "Content of the certificate in a Base64 format."
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Description of the object"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str

    format:
      description: "CertificateFormat of the certificate and private key, possible values: cer,crt,pem,pfx,p12.
      type: str
Required when passing inline certificate content with --certificate-data or --key-data, otherwise format is derived from the file extension."
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict

    key:
      description: "The name of a key to use to encrypt the certificate's key (if empty, the
      type: str
account default protectionKey key will be used)"
      type: str
    key_data:
      description: "Content of the certificate's private key in a Base64 format."
      type: str
    name:
      description: "Certificate name"
      type: str
      required: true
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create certificate
  certificate:
    state: present

- name: Delete certificate
  certificate:
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
    'certificate_data': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'description': {'type': 'str'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'format': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'key': {'type': 'str', 'no_log': False},
    'key_data': {'type': 'str', 'no_log': True},
    'name': {'type': 'str', 'required': True},
    'tags': {'type': 'list', 'elements': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='certificate',
        sdk_create=('CreateCertificate', 'create_certificate'),
        sdk_update=('UpdateCertificateValue', 'update_certificate_value'),
        sdk_delete=('DeleteItem', 'delete_item'),
        sdk_read=('GetCertificateValue', 'get_certificate_value'),
    )


if __name__ == '__main__':
    main()
