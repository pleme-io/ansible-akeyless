#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: usc
short_description: Manages a universal secrets connector (USC) in Akeyless Vault
description:
  - Manage usc resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    binary_value:
      description: "Use this option if the universal secrets value is a base64 encoded binary"
      type: bool
    description:
      description: "Description of the universal secrets"
      type: str
    namespace:
      description: "The namespace (relevant for Hashi vault target)"
      type: str
    object_type:
      description: ""
      type: str
    pfx_password:
      description: "Optional, the passphrase that protects the private key within the pfx certificate (Relevant only for Azure KV certificates)"
      type: str
    region:
      description: "Optional, create secret in a specific region (GCP only).
If empty, a global secret will be created (provider default)."
      type: str
    secret_name:
      description: "Name for the new universal secrets"
      type: str
      required: true
    tags:
      description: "Tags for the universal secrets"
      type: dict
    usc_encryption_key:
      description: "Optional, The name of the remote key that used to encrypt the secret value (if empty, the default key will be used)"
      type: str
    usc_name:
      description: "Name of the Universal Secrets Connector item"
      type: str
      required: true
    value:
      description: "Value of the universal secrets item, either text or base64 encoded binary"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create usc
  usc:
    state: present

- name: Delete usc
  usc:
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
    body = build_body("UscCreate", dict(module.params, token=token))
    return call_api(module, client, "usc_create", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UscUpdate", dict(module.params, token=token))
    return call_api(module, client, "usc_update", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("UscDelete", dict(module.params, token=token))
    return call_api(module, client, "usc_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("UscGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "usc_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'binary_value': {'type': 'bool'},
        'description': {'type': 'str'},
        'namespace': {'type': 'str'},
        'object_type': {'type': 'str'},
        'pfx_password': {'type': 'str'},
        'region': {'type': 'str'},
        'secret_name': {'type': 'str', 'required': True},
        'tags': {'type': 'dict'},
        'usc_encryption_key': {'type': 'str'},
        'usc_name': {'type': 'str', 'required': True},
        'value': {'type': 'str', 'required': True},
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
        module.exit_json(changed=False, msg="usc already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
