#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_gitlab
short_description: Manages a GitLab target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_gitlab resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    gitlab_access_token:
      description: "GitLab personal access token"
      type: str
    gitlab_certificate:
      description: "GitLab TLS certificate (PEM)"
      type: str
    gitlab_url:
      description: "GitLab URL (for self-hosted)"
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
'''

EXAMPLES = r'''
- name: Create target_gitlab
  target_gitlab:
    state: present

- name: Delete target_gitlab
  target_gitlab:
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
    'description': {'type': 'str'},
    'gitlab_access_token': {'type': 'str', 'no_log': True},
    'gitlab_certificate': {'type': 'str', 'no_log': True},
    'gitlab_url': {'type': 'str'},
    'key': {'type': 'str', 'no_log': False},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='target_gitlab',
        sdk_create=('TargetCreateGitlab', 'target_create_gitlab'),
        sdk_update=('TargetUpdateGitlab', 'target_update_gitlab'),
        sdk_delete=('TargetDelete', 'target_delete'),
        sdk_read=('TargetGet', 'target_get'),
    )


if __name__ == '__main__':
    main()
