#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_aws
short_description: Manages an AWS target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_key:
      description: "AWS secret access key"
      type: str
      required: true
    access_key_id:
      description: "AWS access key ID"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    generate_external_id:
      description: "A unique auto-generated value used in your AWS account when configuring your AWS IAM role to securely delegate access to Akeyless. Relevant only when using GW cloud ID"
      type: bool
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
    region:
      description: "AWS region"
      type: str
    role_arn:
      description: "AWS IAM role identifier that Gateway will assume in your AWS account, relevant only when using external ID"
      type: str
    session_token:
      description: "AWS session token (for temporary credentials)"
      type: str
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_aws
  target_aws:
    state: present

- name: Delete target_aws
  target_aws:
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
    body = build_body("TargetCreateAws", dict(module.params, token=token))
    return call_api(module, client, "target_create_aws", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateAws", dict(module.params, token=token))
    return call_api(module, client, "target_update_aws", body)


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
        'access_key': {'type': 'str', 'required': True, 'no_log': True},
        'access_key_id': {'type': 'str', 'required': True, 'no_log': True},
        'description': {'type': 'str'},
        'generate_external_id': {'type': 'bool'},
        'key': {'type': 'str', 'no_log': False},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'region': {'type': 'str'},
        'role_arn': {'type': 'str'},
        'session_token': {'type': 'str', 'no_log': True},
        'use_gw_cloud_identity': {'type': 'bool'},
        'gateway_url': {'type': 'str'},
        'access_id': {'type': 'str'},
        # NOTE: no auth-side `access_key` here -- the resource field above
        # shadows it (resource `access_key` is the AWS secret access key).
        # Auth `access_key` comes from AKEYLESS_ACCESS_KEY env.
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
            module.exit_json(changed=False, msg="target_aws already absent")
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
        module.exit_json(changed=False, msg="target_aws already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
