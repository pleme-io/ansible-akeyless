#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_syslog
short_description: Manages the syslog log forwarding configuration on the gateway (singleton)
description:
  - Manage gateway_log_forwarding_syslog resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    enable_tls:
      description: "Enable tls relevant only for network type TCP"
      type: bool
    formatter:
      description: "Syslog formatter [text/cef]"
      type: str
    host:
      description: "Syslog host"
      type: str
    network:
      description: "Syslog network [tcp/udp]"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    target_tag:
      description: "Syslog target tag"
      type: str
    tls_certificate:
      description: "Syslog tls certificate"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_syslog
  gateway_log_forwarding_syslog:
    state: present

- name: Delete gateway_log_forwarding_syslog
  gateway_log_forwarding_syslog:
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
    body = build_body("GatewayUpdateLogForwardingSyslog", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_syslog", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateLogForwardingSyslog", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_syslog", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayUpdateLogForwardingSyslog", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_syslog", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetLogForwarding", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_log_forwarding", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'enable': {'type': 'str'},
        'enable_tls': {'type': 'bool'},
        'formatter': {'type': 'str'},
        'host': {'type': 'str'},
        'network': {'type': 'str'},
        'output_format': {'type': 'str'},
        'pull_interval': {'type': 'str'},
        'target_tag': {'type': 'str'},
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

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="gateway_log_forwarding_syslog already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
