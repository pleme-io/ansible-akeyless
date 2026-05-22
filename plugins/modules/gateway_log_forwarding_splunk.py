#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_splunk
short_description: Manages the Splunk log forwarding configuration on the gateway (singleton)
description:
  - Manage gateway_log_forwarding_splunk resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    enable_batch:
      description: "Enable batch forwarding [true/false]"
      type: str
    enable_tls:
      description: "Enable tls"
      type: bool
    index:
      description: "Splunk index"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    source:
      description: "Splunk source"
      type: str
    source_type:
      description: "Splunk source type"
      type: str
    splunk_token:
      description: "Splunk token"
      type: str
    splunk_url:
      description: "Splunk server URL"
      type: str
    tls_certificate:
      description: "Splunk tls certificate"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_splunk
  gateway_log_forwarding_splunk:
    state: present

- name: Delete gateway_log_forwarding_splunk
  gateway_log_forwarding_splunk:
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
    body = build_body("GatewayUpdateLogForwardingSplunk", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_splunk", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateLogForwardingSplunk", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_splunk", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayUpdateLogForwardingSplunk", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_splunk", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetLogForwarding", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_log_forwarding", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'enable': {'type': 'str'},
        'enable_batch': {'type': 'str'},
        'enable_tls': {'type': 'bool'},
        'index': {'type': 'str'},
        'output_format': {'type': 'str'},
        'pull_interval': {'type': 'str'},
        'source': {'type': 'str'},
        'source_type': {'type': 'str'},
        'splunk_token': {'type': 'str'},
        'splunk_url': {'type': 'str'},
        'tls_certificate': {'type': 'str'},
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
            module.exit_json(changed=False, msg="gateway_log_forwarding_splunk already absent")
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
        module.exit_json(changed=False, msg="gateway_log_forwarding_splunk already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
