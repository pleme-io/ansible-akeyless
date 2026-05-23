#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_openai
short_description: Manages an OpenAI target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_openai resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "API key for OpenAI"
      type: str
    api_key_id:
      description: "API key ID"
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
    model:
      description: "Default model to use with OpenAI"
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    openai_url:
      description: "Base URL of the OpenAI API"
      type: str
    organization_id:
      description: "Organization ID"
      type: str
'''

EXAMPLES = r'''
- name: Create target_openai
  target_openai:
    state: present

- name: Delete target_openai
  target_openai:
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
    'api_key': {'type': 'str'},
    'api_key_id': {'type': 'str'},
    'description': {'type': 'str'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'model': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'openai_url': {'type': 'str'},
    'organization_id': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_openai",
        sdk_create=("TargetCreateOpenAI", "target_create_open_ai"),
        sdk_update=("TargetUpdateOpenAI", "target_update_open_ai"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
