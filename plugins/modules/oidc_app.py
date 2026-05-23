#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: oidc_app
short_description: Manages an OIDC application in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage oidc_app resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    accessibility:
      description: "for personal password manager"
      type: str
    audience:
      description: "A comma separated list of allowed audiences"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key:
      description: "The name of a key that used to encrypt the OIDC application (if empty, the account default protectionKey key will be used)"
      type: str
    name:
      description: "OIDC application name"
      type: str
      required: true
    permission_assignment:
      description: "A json string defining the access permission assignment for this app"
      type: str
    public:
      description: "Set to true if the app is public (cannot keep secrets)"
      type: bool
    redirect_uris:
      description: "A comma separated list of allowed redirect uris"
      type: str
    scopes:
      description: "A comma separated list of allowed scopes"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create oidc_app
  oidc_app:
    state: present

- name: Delete oidc_app
  oidc_app:
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
    body = build_body("CreateOidcApp", dict(module.params, token=token))
    return call_api(module, client, "create_oidc_app", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdateOidcApp", dict(module.params, token=token))
    return call_api(module, client, "update_oidc_app", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteItem", dict(module.params, token=token))
    return call_api(module, client, "delete_item", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DescribeItem", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "describe_item", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'accessibility': {'type': 'str'},
        'audience': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'key': {'type': 'str', 'no_log': False},
        'name': {'type': 'str', 'required': True},
        'permission_assignment': {'type': 'str'},
        'public': {'type': 'bool'},
        'redirect_uris': {'type': 'str'},
        'scopes': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
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
            module.exit_json(changed=False, msg="oidc_app already absent")
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
        module.exit_json(changed=False, msg="oidc_app already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
