#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_artifactory
short_description: Manages an Artifactory gateway producer (deprecated; prefer akeyless_dynamic_secret_artifactory)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_artifactory resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    artifactory_admin_name:
      description: "Artifactory Admin Name"
      type: str
    artifactory_admin_pwd:
      description: "Artifactory Admin password"
      type: str
    artifactory_token_audience:
      description: "Token Audience"
      type: str
      required: true
    artifactory_token_scope:
      description: "Token Scope"
      type: str
      required: true
    base_url:
      description: "Base URL"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
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
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_artifactory
  gateway_producer_artifactory:
    state: present

- name: Delete gateway_producer_artifactory
  gateway_producer_artifactory:
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
    'artifactory_admin_pwd': {'type': 'str'},
    'artifactory_token_audience': {'type': 'str', 'required': True},
    'artifactory_token_scope': {'type': 'str', 'required': True},
    'base_url': {'type': 'str'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'str'},
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
        resource_label="gateway_producer_artifactory",
        sdk_create=("GatewayCreateProducerArtifactory", "gateway_create_producer_artifactory"),
        sdk_update=("GatewayUpdateProducerArtifactory", "gateway_update_producer_artifactory"),
        sdk_delete=("GatewayDeleteProducer", "gateway_delete_producer"),
        sdk_read=("GatewayGetProducer", "gateway_get_producer"),
    )


if __name__ == '__main__':
    main()
