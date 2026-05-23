#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_forwarder_teams
short_description: Manages a Microsoft Teams event forwarder in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage event_forwarder_teams resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    auth_methods_event_source_locations:
      description: "Auth Method Event sources"
      type: list
      elements: str
    description:
      description: "Description of the object"
      type: str
    event_types:
      description: "List of event types to notify about [request-access, certificate-pending-expiration, certificate-expired, certificate-provisioning-success, certificate-provisioning-failure, auth-method-pending-expiration, auth-method-expired, next-automatic-rotation, rotated-secret-success, rotated-secret-failure, dynamic-secret-failure, multi-auth-failure, uid-rotation-failure, apply-justification, email-auth-method-approved, usage, rotation-usage, gateway-inactive, static-secret-updated, rate-limiting, usage-report, secret-sync]"
      type: list
      elements: str
    every:
      description: "Rate of periodic runner repetition in hours"
      type: str
    gateways_event_source_locations:
      description: "Event sources"
      type: list
      required: true
      elements: str
    items_event_source_locations:
      description: "Items Event sources"
      type: list
      elements: str
    key:
      description: "The name of a key that used to encrypt the EventForwarder secret value (if empty, the account default protectionKey key will be used)"
      type: str
    name:
      description: "EventForwarder name"
      type: str
      required: true
    runner_type:
      description: ""
      type: str
      required: true
    targets_event_source_locations:
      description: "Targets Event sources"
      type: list
      elements: str
    url:
      description: "Teams Webhook URL"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create event_forwarder_teams
  event_forwarder_teams:
    state: present

- name: Delete event_forwarder_teams
  event_forwarder_teams:
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
    body = build_body("EventForwarderCreateTeams", dict(module.params, token=token))
    return call_api(module, client, "event_forwarder_create_teams", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("EventForwarderUpdateTeams", dict(module.params, token=token))
    return call_api(module, client, "event_forwarder_update_teams", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("EventForwarderDelete", dict(module.params, token=token))
    return call_api(module, client, "event_forwarder_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GetEventForwarder", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "get_event_forwarder", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'auth_methods_event_source_locations': {'type': 'list', 'elements': 'str'},
        'description': {'type': 'str'},
        'event_types': {'type': 'list', 'elements': 'str'},
        'every': {'type': 'str'},
        'gateways_event_source_locations': {'type': 'list', 'required': True, 'elements': 'str'},
        'items_event_source_locations': {'type': 'list', 'elements': 'str'},
        'key': {'type': 'str', 'no_log': False},
        'name': {'type': 'str', 'required': True},
        'runner_type': {'type': 'str', 'required': True},
        'targets_event_source_locations': {'type': 'list', 'elements': 'str'},
        'url': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="event_forwarder_teams already absent")
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
        module.exit_json(changed=False, msg="event_forwarder_teams already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
