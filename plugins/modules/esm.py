#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: esm
short_description: Manages an external secrets manager (ESM) in Akeyless Vault
description:
  - Manage esm resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    binary_value:
      description: "Use this option if the external secret value is a base64 encoded binary"
      type: bool
    description:
      description: "Description of the external secret"
      type: str
    esm_name:
      description: "Name of the External Secrets Manager item"
      type: str
      required: true
    secret_name:
      description: "Name for the new external secret"
      type: str
      required: true
    tags:
      description: "Tags for the external secret"
      type: dict
    value:
      description: "Value of the external secret item, either text or base64 encoded binary"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create esm
  esm:
    state: present

- name: Delete esm
  esm:
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
    body = build_body("EsmCreate", dict(module.params, token=token))
    return call_api(module, client, "esm_create", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("EsmUpdate", dict(module.params, token=token))
    return call_api(module, client, "esm_update", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("EsmDelete", dict(module.params, token=token))
    return call_api(module, client, "esm_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("EsmGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "esm_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'binary_value': {'type': 'bool'},
        'description': {'type': 'str'},
        'esm_name': {'type': 'str', 'required': True},
        'secret_name': {'type': 'str', 'required': True},
        'tags': {'type': 'dict'},
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
        module.exit_json(changed=False, msg="esm already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
