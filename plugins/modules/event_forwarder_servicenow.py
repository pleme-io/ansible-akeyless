#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_forwarder_servicenow
short_description: Manages a ServiceNow event forwarder in Akeyless Vault
description:
  - Manage event_forwarder_servicenow resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    admin_name:
      description: "Workstation Admin Name"
      type: str
    admin_pwd:
      description: "Workstation Admin Password"
      type: str
    app_private_key_base64:
      description: "The RSA Private Key to use when connecting with jwt authentication"
      type: str
    auth_methods_event_source_locations:
      description: "Auth Method Event sources"
      type: list
      elements: str
    auth_type:
      description: "The authentication type to use [user-pass/jwt]"
      type: str
    client_id:
      description: "The client ID to use when connecting with jwt authentication"
      type: str
    client_secret:
      description: "The client secret to use when connecting with jwt authentication"
      type: str
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
    host:
      description: "Workstation Host"
      type: str
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
    user_email:
      description: "The user email to identify with when connecting with jwt authentication"
      type: str
'''

EXAMPLES = r'''
- name: Create event_forwarder_servicenow
  event_forwarder_servicenow:
    state: present

- name: Delete event_forwarder_servicenow
  event_forwarder_servicenow:
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
    body = build_body("EventForwarderCreateServiceNow", dict(module.params, token=token))
    return call_api(module, client, "event_forwarder_create_service_now", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("EventForwarderUpdateServiceNow", dict(module.params, token=token))
    return call_api(module, client, "event_forwarder_update_service_now", body)


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
        'admin_name': {'type': 'str'},
        'admin_pwd': {'type': 'str'},
        'app_private_key_base64': {'type': 'str'},
        'auth_methods_event_source_locations': {'type': 'list', 'elements': 'str'},
        'auth_type': {'type': 'str'},
        'client_id': {'type': 'str'},
        'client_secret': {'type': 'str'},
        'description': {'type': 'str'},
        'event_types': {'type': 'list', 'elements': 'str'},
        'every': {'type': 'str'},
        'gateways_event_source_locations': {'type': 'list', 'required': True, 'elements': 'str'},
        'host': {'type': 'str'},
        'items_event_source_locations': {'type': 'list', 'elements': 'str'},
        'key': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'runner_type': {'type': 'str', 'required': True},
        'targets_event_source_locations': {'type': 'list', 'elements': 'str'},
        'user_email': {'type': 'str'},
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
        module.exit_json(changed=False, msg="event_forwarder_servicenow already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
