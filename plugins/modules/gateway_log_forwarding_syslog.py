#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_syslog
short_description: Manages the syslog log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_syslog",
        sdk_create=("GatewayUpdateLogForwardingSyslog", "gateway_update_log_forwarding_syslog"),
        sdk_update=("GatewayUpdateLogForwardingSyslog", "gateway_update_log_forwarding_syslog"),
        sdk_delete=("GatewayUpdateLogForwardingSyslog", "gateway_update_log_forwarding_syslog"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
