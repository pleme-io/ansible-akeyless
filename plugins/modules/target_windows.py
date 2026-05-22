#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_windows
short_description: Manages a Windows target in Akeyless Vault
description:
  - Manage target_windows resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate:
      description: "Client certificate (PEM)"
      type: str
      no_log: true
    connection_type:
      description: "Type of connection to Windows Server [credentials/parent-target]"
      type: str
    description:
      description: "Target description"
      type: str
    domain:
      description: "Windows domain"
      type: str
    hostname:
      description: "Windows host address"
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
    parent_target_name:
      description: "Name of the parent target, relevant only when connection-type is parent-target"
      type: str
    port:
      description: "WinRM port (default: 5986)"
      type: str
    use_tls:
      description: "Use TLS for WinRM connection"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_windows
  target_windows:
    state: present

- name: Delete target_windows
  target_windows:
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
    body = build_body("TargetCreateWindows", dict(module.params, token=token))
    return call_api(module, client, "target_create_windows", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateWindows", dict(module.params, token=token))
    return call_api(module, client, "target_update_windows", body)


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
        'certificate': {'type': 'str', 'no_log': True},
        'connection_type': {'type': 'str'},
        'description': {'type': 'str'},
        'domain': {'type': 'str'},
        'hostname': {'type': 'str', 'required': True},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'parent_target_name': {'type': 'str'},
        'password': {'type': 'str', 'no_log': True, 'required': True},
        'port': {'type': 'str'},
        'use_tls': {'type': 'bool'},
        'username': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="target_windows already absent")
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
        module.exit_json(changed=False, msg="target_windows already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
