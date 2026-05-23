#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_github
short_description: Manages a GitHub gateway producer (deprecated; prefer akeyless_dynamic_secret_github)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_github resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    github_app_id:
      description: "Github app id"
      type: int
    github_app_private_key:
      description: "App private key"
      type: str
    github_base_url:
      description: "Base URL"
      type: str
    installation_id:
      description: "GitHub application installation id"
      type: int
    installation_organization:
      description: "Optional, mutually exclusive with installation id, GitHub organization name"
      type: str
    installation_repository:
      description: "Optional, mutually exclusive with installation id, GitHub repository '<owner>/<repo-name>'"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    token_permissions:
      description: "Optional - installation token's allowed permissions"
      type: list
      elements: str
    token_repositories:
      description: "Optional - installation token's allowed repositories"
      type: list
      elements: str
    token_ttl:
      description: "Token TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_github
  gateway_producer_github:
    state: present

- name: Delete gateway_producer_github
  gateway_producer_github:
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
    'delete_protection': {'type': 'str'},
    'github_app_id': {'type': 'int'},
    'github_app_private_key': {'type': 'str'},
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
        resource_label="gateway_producer_github",
        sdk_create=("GatewayCreateProducerGithub", "gateway_create_producer_github"),
        sdk_update=("GatewayUpdateProducerGithub", "gateway_update_producer_github"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
