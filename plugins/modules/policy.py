#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: policy
short_description: Manages a policy in Akeyless Vault
description:
  - Manage policy resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    allowed_algorithms:
      description: "Specify allowed key algorithms (e.g., [RSA2048,AES128GCM])"
      type: list
      elements: str
    allowed_key_names:
      description: "Specify allowed protection key names. To enforce using the account's default protection key, use 'default-account-key'"
      type: list
      elements: str
    allowed_key_types:
      description: "Specify allowed key protection types (dfc, classic-key)"
      type: list
      elements: str
    max_rotation_interval_days:
      description: "Set the maximum rotation interval for automatic key rotation."
      type: int
    object_types:
      description: "The object types this policy will apply to (items, targets). If not provided, defaults to [items, targets]."
      type: list
      elements: str
    path:
      description: "The path the policy refers to"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create policy
  policy:
    state: present

- name: Delete policy
  policy:
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
    body = build_body("PolicyCreateKeys", dict(module.params, token=token))
    return call_api(module, client, "policy_create_keys", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("PolicyUpdateKeys", dict(module.params, token=token))
    return call_api(module, client, "policy_update_keys", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("PoliciesDelete", dict(module.params, token=token))
    return call_api(module, client, "policies_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("PoliciesGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "policies_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'allowed_algorithms': {'type': 'list', 'elements': 'str'},
        'allowed_key_names': {'type': 'list', 'elements': 'str'},
        'allowed_key_types': {'type': 'list', 'elements': 'str'},
        'max_rotation_interval_days': {'type': 'int'},
        'object_types': {'type': 'list', 'elements': 'str'},
        'path': {'type': 'str', 'required': True},
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
        module.exit_json(changed=False, msg="policy already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
