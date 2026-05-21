#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_google_chronicle
short_description: Manages the Google Chronicle log forwarding configuration on the gateway (singleton)
description:
  - Manage gateway_log_forwarding_google_chronicle resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    customer_id:
      description: "Google chronicle customer id"
      type: str
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    gcp_key:
      description: "Base64-encoded service account private key text"
      type: str
    log_type:
      description: "Google chronicle log type"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    region:
      description: "Google chronicle region [eu_multi_region/london/us_multi_region/singapore/tel_aviv]"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_google_chronicle
  gateway_log_forwarding_google_chronicle:
    state: present

- name: Delete gateway_log_forwarding_google_chronicle
  gateway_log_forwarding_google_chronicle:
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
    body = build_body("GatewayUpdateLogForwardingGoogleChronicle", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_google_chronicle", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateLogForwardingGoogleChronicle", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_google_chronicle", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayUpdateLogForwardingGoogleChronicle", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_google_chronicle", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetLogForwarding", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_log_forwarding", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'customer_id': {'type': 'str'},
        'enable': {'type': 'str'},
        'gcp_key': {'type': 'str'},
        'log_type': {'type': 'str'},
        'output_format': {'type': 'str'},
        'pull_interval': {'type': 'str'},
        'region': {'type': 'str'},
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
        module.exit_json(changed=False, msg="gateway_log_forwarding_google_chronicle already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
