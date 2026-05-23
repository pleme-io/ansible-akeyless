#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_gitlab
short_description: Manages a GitLab dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_gitlab resources.
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
    gitlab_access_token:
      description: "GitLab personal access token"
      type: str
    gitlab_access_type:
      description: "GitLab access type: personal or project"
      type: str
      required: true
    gitlab_certificate:
      description: "GitLab TLS certificate (PEM)"
      type: str
    gitlab_role:
      description: "GitLab role for dynamic tokens"
      type: str
    gitlab_token_scopes:
      description: "GitLab token scopes (comma-separated)"
      type: str
      required: true
    gitlab_url:
      description: "GitLab URL (for self-hosted)"
      type: str
    group_name:
      description: "GitLab group name"
      type: str
    installation_organization:
      description: "GitLab organization"
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
    ttl:
      description: "Access Token TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_gitlab
  dynamic_secret_gitlab:
    state: present

- name: Delete dynamic_secret_gitlab
  dynamic_secret_gitlab:
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
    'gitlab_access_token': {'type': 'str', 'no_log': True},
    'gitlab_access_type': {'type': 'str', 'required': True},
    'gitlab_certificate': {'type': 'str', 'no_log': True},
    'gitlab_role': {'type': 'str'},
    'gitlab_token_scopes': {'type': 'str', 'required': True},
    'gitlab_url': {'type': 'str'},
    'group_name': {'type': 'str'},
    'installation_organization': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_gitlab",
        sdk_create=("DynamicSecretCreateGitlab", "dynamic_secret_create_gitlab"),
        sdk_update=("DynamicSecretUpdateGitlab", "dynamic_secret_update_gitlab"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
