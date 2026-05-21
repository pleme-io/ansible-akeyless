#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_godaddy
short_description: Manages a GoDaddy target in Akeyless Vault
description:
  - Manage target_godaddy resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "GoDaddy API key"
      type: str
      required: true
      no_log: true
    customer_id:
      description: "Customer ID (ShopperId) required for renewal of imported certificates"
      type: str
    description:
      description: "Target description"
      type: str
    imap_fqdn:
      description: "IMAP server FQDN for domain validation"
      type: str
      required: true
    imap_password:
      description: "IMAP password"
      type: str
      required: true
      no_log: true
    imap_port:
      description: "IMAP server port"
      type: str
    imap_username:
      description: "IMAP username"
      type: str
      required: true
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
    secret:
      description: "GoDaddy API secret"
      type: str
      required: true
      no_log: true
    timeout:
      description: "GoDaddy API timeout"
      type: str
'''

EXAMPLES = r'''
- name: Create target_godaddy
  target_godaddy:
    state: present

- name: Delete target_godaddy
  target_godaddy:
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
    body = build_body("TargetCreateGodaddy", dict(module.params, token=token))
    return call_api(module, client, "target_create_godaddy", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateGodaddy", dict(module.params, token=token))
    return call_api(module, client, "target_update_godaddy", body)


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
        'api_key': {'type': 'str', 'required': True, 'no_log': True},
        'customer_id': {'type': 'str'},
        'description': {'type': 'str'},
        'imap_fqdn': {'type': 'str', 'required': True},
        'imap_password': {'type': 'str', 'required': True, 'no_log': True},
        'imap_port': {'type': 'str'},
        'imap_username': {'type': 'str', 'required': True},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'secret': {'type': 'str', 'required': True, 'no_log': True},
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
        module.exit_json(changed=False, msg="target_godaddy already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
