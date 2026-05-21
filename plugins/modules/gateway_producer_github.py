#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_github
short_description: Manages a GitHub gateway producer (deprecated; prefer akeyless_dynamic_secret_github)
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayCreateProducerGithub", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_github", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerGithub", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_github", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="gateway_producer_github already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
