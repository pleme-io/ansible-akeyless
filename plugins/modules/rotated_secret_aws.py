#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: rotated_secret_aws
short_description: Manages an AWS rotated secret
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage rotated_secret_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_id:
      description: "API ID to rotate (relevant only for rotator-type=api-key)"
      type: str
    api_key:
      description: "API key to rotate (relevant only for rotator-type=api-key)"
      type: str
    authentication_credentials:
      description: "Credentials to connect with: use-user-creds or use-target-creds"
      type: str
    auto_rotate:
      description: "Whether to automatically rotate every rotation-interval days [true/false]"
      type: str
    aws_region:
      description: "AWS region"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    grace_rotation:
      description: "Enable graceful rotation [true/false]"
      type: str
    grace_rotation_hour:
      description: "The Hour of the grace rotation in UTC"
      type: int
    grace_rotation_interval:
      description: "Days to wait before deleting the old key"
      type: str
    grace_rotation_timing:
      description: "When to create the new version relative to the rotation date [after/before]"
      type: str
    key:
      description: "Encryption key name for the secret value"
      type: str
    max_versions:
      description: "Maximum number of versions"
      type: str
    name:
      description: "Rotated secret name"
      type: str
      required: true
    password_length:
      description: "Length of the password to be generated"
      type: str
    rotate_after_disconnect:
      description: "Rotate after SRA session ends [true/false]"
      type: str
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_hour:
      description: "The hour of the rotation in UTC"
      type: int
    rotation_interval:
      description: "Days between every automatic key rotation (1-365)"
      type: str
    rotator_type:
      description: "The rotator type: target or api-key"
      type: str
      required: true
    tags:
      description: "Tags for the rotated secret"
      type: list
      elements: str
    target_name:
      description: "Target name to associate"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create rotated_secret_aws
  rotated_secret_aws:
    state: present

- name: Delete rotated_secret_aws
  rotated_secret_aws:
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
    body = build_body("RotatedSecretCreateAws", dict(module.params, token=token))
    return call_api(module, client, "rotated_secret_create_aws", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("RotatedSecretUpdateAws", dict(module.params, token=token))
    return call_api(module, client, "rotated_secret_update_aws", body)


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
        'api_id': {'type': 'str'},
        'api_key': {'type': 'str', 'no_log': True},
        'authentication_credentials': {'type': 'str'},
        'auto_rotate': {'type': 'str'},
        'aws_region': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'grace_rotation': {'type': 'str'},
        'grace_rotation_hour': {'type': 'int'},
        'grace_rotation_interval': {'type': 'str'},
        'grace_rotation_timing': {'type': 'str'},
        'key': {'type': 'str', 'no_log': False},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str', 'no_log': False},
        'rotate_after_disconnect': {'type': 'str'},
        'rotation_event_in': {'type': 'list', 'elements': 'str'},
        'rotation_hour': {'type': 'int'},
        'rotation_interval': {'type': 'str'},
        'rotator_type': {'type': 'str', 'required': True},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="rotated_secret_aws already absent")
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
        module.exit_json(changed=False, msg="rotated_secret_aws already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
