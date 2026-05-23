#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_forwarder_slack
short_description: Manages a Slack event forwarder in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage event_forwarder_slack resources.
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
      description: "Slack Webhook URL"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create event_forwarder_slack
  event_forwarder_slack:
    state: present

- name: Delete event_forwarder_slack
  event_forwarder_slack:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='event_forwarder_slack',
        sdk_create=('EventForwarderCreateSlack', 'event_forwarder_create_slack'),
        sdk_update=('EventForwarderUpdateSlack', 'event_forwarder_update_slack'),
        sdk_delete=('EventForwarderDelete', 'event_forwarder_delete'),
        sdk_read=('GetEventForwarder', 'get_event_forwarder'),
    )


if __name__ == '__main__':
    main()
