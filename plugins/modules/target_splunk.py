#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_splunk
short_description: Manages a Splunk target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_splunk resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    audience:
      description: "Splunk token audience (required when using token authentication for rotation)"
      type: str
    description:
      description: "Target description"
      type: str
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
    token_owner:
      description: "Splunk Token Owner (required when using token authentication for rotation)"
      type: str
    url:
      description: "Splunk server URL"
      type: str
      required: true
    use_tls:
      description: "Use TLS certificate verification when connecting to the Splunk management API"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_splunk
  target_splunk:
    state: present

- name: Delete target_splunk
  target_splunk:
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
    'audience': {'type': 'str'},
    'description': {'type': 'str'},
    'key': {'type': 'str', 'no_log': False},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'token_owner': {'type': 'str', 'no_log': False},
    'url': {'type': 'str', 'required': True},
    'use_tls': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_splunk',
        sdk_create=('TargetCreateSplunk', 'target_create_splunk'),
        sdk_update=None,
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
        immutable=True,
    )


if __name__ == '__main__':
    main()
