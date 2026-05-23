#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ssh_cert_issuer
short_description: Manages an SSH certificate issuer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage ssh_cert_issuer resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    ProviderType:
      description: ""
      type: str
    allowed_users:
      description: "Users allowed to fetch the certificate, e.g. root,ubuntu"
      type: str
      required: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    extensions:
      description: "Signed certificates with extensions, e.g. permit-port-forwarding"
      type: dict
    external_username:
      description: "Externally provided username [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "Key-name of IdP claim to extract username from (for external-username=true)"
      type: str
    host_provider:
      description: "Host provider type [explicit/target]"
      type: str
    name:
      description: "SSH certificate issuer name"
      type: str
      required: true
    principals:
      description: "Signed certificates with principal, e.g. example_role1,example_role2"
      type: str
    secure_access_use_internal_ssh_access:
      description: "Use internal SSH Access"
      type: bool
    signer_key_name:
      description: "Key to sign the certificate with"
      type: str
      required: true
    tag:
      description: "Tags for the SSH cert issuer"
      type: list
      elements: str
    target:
      description: "A list of linked targets to be associated, Relevant only for Secure Remote Access for ssh cert issuer, ldap rotated secret and ldap dynamic secret, To specify multiple targets use argument multiple times"
      type: list
      elements: str
    ttl:
      description: "Certificate TTL in seconds"
      type: int
      required: true
'''

EXAMPLES = r'''
- name: Create ssh_cert_issuer
  ssh_cert_issuer:
    state: present

- name: Delete ssh_cert_issuer
  ssh_cert_issuer:
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
    'allowed_users': {'type': 'str', 'required': True},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'extensions': {'type': 'dict'},
    'external_username': {'type': 'str'},
    'fixed_user_claim_keyname': {'type': 'str'},
    'host_provider': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'principals': {'type': 'str'},
    'secure_access_use_internal_ssh_access': {'type': 'bool'},
    'signer_key_name': {'type': 'str', 'required': True},
    'tag': {'type': 'list', 'elements': 'str'},
    'target': {'type': 'list', 'elements': 'str'},
    'ttl': {'type': 'int', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="ssh_cert_issuer",
        sdk_create=("CreateSSHCertIssuer", "create_ssh_cert_issuer"),
        sdk_update=("UpdateSSHCertIssuer", "update_ssh_cert_issuer"),
        sdk_delete=("DeleteItem", "delete_item"),
        sdk_read=("DescribeItem", "describe_item"),
    )


if __name__ == '__main__':
    main()
