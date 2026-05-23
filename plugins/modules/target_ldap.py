#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_ldap
short_description: Manages an LDAP target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_ldap resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    bind_dn:
      description: "LDAP bind DN"
      type: str
      required: true
    bind_dn_password:
      description: "LDAP bind DN password"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    ldap_ca_cert:
      description: "CA Certificate File Content"
      type: str
    ldap_url:
      description: "LDAP server URL (e.g., ldap://host:389)"
      type: str
      required: true
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    server_type:
      description: "Set Ldap server type, Options:[OpenLDAP, ActiveDirectory]. Default is OpenLDAP"
      type: str
    token_expiration:
      description: "LDAP token expiration in seconds"
      type: str
'''

EXAMPLES = r'''
- name: Create target_ldap
  target_ldap:
    state: present

- name: Delete target_ldap
  target_ldap:
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
    'bind_dn': {'type': 'str', 'required': True},
    'bind_dn_password': {'type': 'str', 'required': True, 'no_log': True},
    'description': {'type': 'str'},
    'key': {'type': 'str'},
    'ldap_ca_cert': {'type': 'str'},
    'ldap_url': {'type': 'str', 'required': True},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'server_type': {'type': 'str'},
    'token_expiration': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_ldap",
        sdk_create=("TargetCreateLdap", "target_create_ldap"),
        sdk_update=("TargetUpdateLdap", "target_update_ldap"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
