#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_github
short_description: Manages a GitHub dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_github resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    github_app_id:
      description: "GitHub App ID"
      type: int
    github_app_private_key:
      description: "GitHub App private key (PEM)"
      type: str
    github_base_url:
      description: "GitHub base URL (for GitHub Enterprise)"
      type: str
    installation_id:
      description: "GitHub App installation ID"
      type: int
    installation_organization:
      description: "GitHub organization for installation"
      type: str
    installation_repository:
      description: "GitHub repository for installation"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    token_permissions:
      description: "GitHub token permissions (JSON)"
      type: list
      elements: str
    token_repositories:
      description: "GitHub repositories for token scope (comma-separated)"
      type: list
      elements: str
    token_ttl:
      description: "Token TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_github
  dynamic_secret_github:
    state: present

- name: Delete dynamic_secret_github
  dynamic_secret_github:
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
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'github_app_id': {'type': 'int'},
    'github_app_private_key': {'type': 'str', 'no_log': True},
    'github_base_url': {'type': 'str'},
    'installation_id': {'type': 'int'},
    'installation_organization': {'type': 'str'},
    'installation_repository': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'token_permissions': {'type': 'list', 'elements': 'str'},
    'token_repositories': {'type': 'list', 'elements': 'str'},
    'token_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_github",
        sdk_create=("DynamicSecretCreateGithub", "dynamic_secret_create_github"),
        sdk_update=("DynamicSecretUpdateGithub", "dynamic_secret_update_github"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
