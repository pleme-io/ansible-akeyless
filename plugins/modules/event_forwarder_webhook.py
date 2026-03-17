#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_forwarder_webhook
short_description: Manages a Webhook event forwarder in Akeyless Vault
description:
  - Manage event_forwarder_webhook resources.
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
    auth_token:
      description: "Base64 encoded Token string for authentication type Token"
      type: str
    auth_type:
      description: "The Webhook authentication type [user-pass, bearer-token, certificate]"
      type: str
    client_cert_data:
      description: "Base64 encoded PEM certificate, relevant for certificate auth-type"
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
    private_key_data:
      description: "Base64 encoded PEM RSA Private Key, relevant for certificate auth-type"
      type: str
    runner_type:
      description: ""
      type: str
      required: true
    server_certificates:
      description: "Base64 encoded PEM certificate of the Webhook"
      type: str
    targets_event_source_locations:
      description: "Targets Event sources"
      type: list
      elements: str
    url:
      description: "Webhook URL"
      type: str
'''

EXAMPLES = r'''
- name: Create event_forwarder_webhook
  event_forwarder_webhook:
    state: present

- name: Delete event_forwarder_webhook
  event_forwarder_webhook:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="event_forwarder_webhook created")
    except Exception as e:
        module.fail_json(msg="Failed to create event_forwarder_webhook: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="event_forwarder_webhook updated")
    except Exception as e:
        module.fail_json(msg="Failed to update event_forwarder_webhook: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="event_forwarder_webhook deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete event_forwarder_webhook: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read event_forwarder_webhook: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'auth_methods_event_source_locations': {'type': 'list', 'elements': 'str'},
        'auth_token': {'type': 'str'},
        'auth_type': {'type': 'str'},
        'client_cert_data': {'type': 'str'},
        'description': {'type': 'str'},
        'event_types': {'type': 'list', 'elements': 'str'},
        'every': {'type': 'str'},
        'gateways_event_source_locations': {'type': 'list', 'required': True, 'elements': 'str'},
        'items_event_source_locations': {'type': 'list', 'elements': 'str'},
        'key': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'private_key_data': {'type': 'str'},
        'runner_type': {'type': 'str', 'required': True},
        'server_certificates': {'type': 'str'},
        'targets_event_source_locations': {'type': 'list', 'elements': 'str'},
        'url': {'type': 'str'},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params.get('state', 'present')
    current = read_resource(module)

    if module.check_mode:
        module.exit_json(changed=(current is None and state == 'present')
                         or (current is not None and state == 'absent'))

    if state == 'absent':
        if current is not None:
            delete_resource(module)
        else:
            module.exit_json(changed=False, msg="event_forwarder_webhook already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
