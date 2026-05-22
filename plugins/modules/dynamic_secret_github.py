#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_github
short_description: Manages a GitHub dynamic secret producer
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
      no_log: true
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("DynamicSecretCreateGithub", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_create_github", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("DynamicSecretUpdateGithub", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_update_github", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DynamicSecretDelete", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DynamicSecretGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "dynamic_secret_get", body, swallow_404=True)


def main():
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="dynamic_secret_github already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        result = delete_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # state == 'present'
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = create_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs
    # from what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False, msg="dynamic_secret_github already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
