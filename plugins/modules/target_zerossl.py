#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_zerossl
short_description: Manages a ZeroSSL target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_zerossl resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "ZeroSSL API key"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    imap_fqdn:
      description: "IMAP server FQDN for domain validation"
      type: str
      required: true
    imap_password:
      description: "IMAP password"
      type: str
      required: true
    imap_port:
      description: "IMAP server port"
      type: str
    imap_target_email:
      description: "Target email for domain validation"
      type: str
    imap_username:
      description: "IMAP username"
      type: str
      required: true
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    timeout:
      description: "Timeout waiting for certificate validation in Duration format (1h - 1 Hour, 20m - 20 Minutes, 33m3s - 33 Minutes and 3 Seconds), maximum 1h."
      type: str
'''

EXAMPLES = r'''
- name: Create target_zerossl
  target_zerossl:
    state: present

- name: Delete target_zerossl
  target_zerossl:
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
    'api_key': {'type': 'str', 'required': True, 'no_log': True},
    'description': {'type': 'str'},
    'imap_fqdn': {'type': 'str', 'required': True},
    'imap_password': {'type': 'str', 'required': True, 'no_log': True},
    'imap_port': {'type': 'str'},
    'imap_target_email': {'type': 'str'},
    'imap_username': {'type': 'str', 'required': True},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'timeout': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_zerossl",
        sdk_create=("TargetCreateZeroSSL", "target_create_zero_ssl"),
        sdk_update=("TargetUpdateZeroSSL", "target_update_zero_ssl"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
