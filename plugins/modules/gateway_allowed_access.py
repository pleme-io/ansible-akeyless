#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_allowed_access
short_description: Manages gateway allowed access in Akeyless
description:
  - Manage gateway_allowed_access resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    SubClaimsCaseInsensitive:
      description: ""
      type: bool
    access_id:
      description: "The access ID to attach to this allowed access"
      type: str
      required: true
    case_sensitive:
      description: "Treat sub claims as case-sensitive [true/false]"
      type: str
    description:
      description: "Allowed access description"
      type: str
    name:
      description: "Allowed access name"
      type: str
      required: true
    permissions:
      description: "Comma-separated list of permissions: defaults, targets, classic_keys, automatic_migration, ldap_auth, dynamic_secret, k8s_auth, log_forwarding, zero_knowledge_encryption, rotated_secret, caching, event_forwarding, admin, kmip, general, rotate_secret_value"
      type: str
    sub_claims:
      description: "Key/val of sub claims, e.g. group=admins,developers"
      type: dict
'''

EXAMPLES = r'''
- name: Create gateway_allowed_access
  gateway_allowed_access:
    state: present

- name: Delete gateway_allowed_access
  gateway_allowed_access:
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
    body = build_body("GatewayCreateAllowedAccess", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_allowed_access", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateAllowedAccess", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_allowed_access", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteAllowedAccess", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_allowed_access", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetAllowedAccess", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_allowed_access", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'SubClaimsCaseInsensitive': {'type': 'bool'},
        'access_id': {'type': 'str', 'required': True},
        'case_sensitive': {'type': 'str'},
        'description': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'permissions': {'type': 'str'},
        'sub_claims': {'type': 'dict'},
        'gateway_url': {'type': 'str'},
        # NOTE: no auth-side `access_id` here -- the resource field above
        # shadows it. Auth `access_id` comes from AKEYLESS_ACCESS_ID env.
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
        module.exit_json(changed=False, msg="gateway_allowed_access already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
