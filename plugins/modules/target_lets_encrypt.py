#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_lets_encrypt
short_description: Manages a Let's Encrypt target in Akeyless Vault
description:
  - Manage target_lets_encrypt resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    acme_challenge:
      description: ""
      type: str
    description:
      description: "Target description"
      type: str
    dns_target_creds:
      description: "Name of existing cloud target for DNS credentials. Required when acme-challenge=dns. Supported: AWS, Azure, GCP targets"
      type: str
    email:
      description: "Email address for ACME account registration"
      type: str
    gcp_project:
      description: "GCP Cloud DNS: Project ID. Optional - can be derived from service account"
      type: str
    hosted_zone:
      description: "AWS Route53 hosted zone ID. Required when dns-target-creds points to AWS target"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    lets_encrypt_url:
      description: ""
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    resource_group:
      description: "Azure resource group name. Required when dns-target-creds points to Azure target"
      type: str
    timeout:
      description: ""
      type: str
'''

EXAMPLES = r'''
- name: Create target_lets_encrypt
  target_lets_encrypt:
    state: present

- name: Delete target_lets_encrypt
  target_lets_encrypt:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("TargetCreateLetsEncrypt", dict(module.params, token=token))
    return call_api(module, client, "target_create_lets_encrypt", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateLetsEncrypt", dict(module.params, token=token))
    return call_api(module, client, "target_update_lets_encrypt", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("TargetDelete", dict(module.params, token=token))
    return call_api(module, client, "target_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("TargetGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "target_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'acme_challenge': {'type': 'str'},
        'description': {'type': 'str'},
        'dns_target_creds': {'type': 'str'},
        'email': {'type': 'str'},
        'gcp_project': {'type': 'str'},
        'hosted_zone': {'type': 'str'},
        'key': {'type': 'str'},
        'lets_encrypt_url': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'resource_group': {'type': 'str'},
        'timeout': {'type': 'str'},
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
        module.exit_json(changed=False, msg="target_lets_encrypt already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
