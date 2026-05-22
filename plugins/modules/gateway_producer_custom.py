#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_custom
short_description: Manages a custom gateway producer (deprecated; prefer akeyless_dynamic_secret_custom)
description:
  - Manage gateway_producer_custom resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    admin_rotation_interval_days:
      description: "Define rotation interval in days"
      type: int
    create_sync_url:
      description: "URL of an endpoint that implements /sync/create method, for example
https://webhook.example.com/sync/create"
      type: str
      required: true
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    enable_admin_rotation:
      description: "Should admin credentials be rotated"
      type: bool
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    payload:
      description: "Secret payload to be sent with each create/revoke webhook request"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    revoke_sync_url:
      description: "URL of an endpoint that implements /sync/revoke method, for example
https://webhook.example.com/sync/revoke"
      type: str
      required: true
    rotate_sync_url:
      description: "URL of an endpoint that implements /sync/rotate method, for example
https://webhook.example.com/sync/rotate"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    timeout_sec:
      description: "Maximum allowed time in seconds for the webhook to return the results"
      type: int
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_custom
  gateway_producer_custom:
    state: present

- name: Delete gateway_producer_custom
  gateway_producer_custom:
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
    body = build_body("GatewayCreateProducerCustom", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_custom", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerCustom", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_custom", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'admin_rotation_interval_days': {'type': 'int'},
        'create_sync_url': {'type': 'str', 'required': True},
        'delete_protection': {'type': 'str'},
        'enable_admin_rotation': {'type': 'bool'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'payload': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'revoke_sync_url': {'type': 'str', 'required': True},
        'rotate_sync_url': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'timeout_sec': {'type': 'int'},
        'user_ttl': {'type': 'str'},
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
            module.exit_json(changed=False, msg="gateway_producer_custom already absent")
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
        module.exit_json(changed=False, msg="gateway_producer_custom already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
