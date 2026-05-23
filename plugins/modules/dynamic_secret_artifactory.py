#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_artifactory
short_description: Manages an Artifactory dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_artifactory resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    artifactory_admin_name:
      description: "Artifactory admin username"
      type: str
    artifactory_admin_pwd:
      description: "Artifactory admin password"
      type: str
      no_log: true
    artifactory_token_audience:
      description: "Artifactory token audience"
      type: str
      required: true
    artifactory_token_scope:
      description: "Artifactory token scope"
      type: str
      required: true
    base_url:
      description: "Artifactory base URL"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_artifactory
  dynamic_secret_artifactory:
    state: present

- name: Delete dynamic_secret_artifactory
  dynamic_secret_artifactory:
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
    'artifactory_admin_name': {'type': 'str'},
    'artifactory_admin_pwd': {'type': 'str', 'no_log': True},
    'artifactory_token_audience': {'type': 'str', 'required': True},
    'artifactory_token_scope': {'type': 'str', 'required': True},
    'base_url': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'producer_encryption_key_name': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_artifactory",
        sdk_create=("DynamicSecretCreateArtifactory", "dynamic_secret_create_artifactory"),
        sdk_update=("DynamicSecretUpdateArtifactory", "dynamic_secret_update_artifactory"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
