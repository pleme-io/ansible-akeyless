#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_datadog
short_description: Manages the Datadog log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_datadog resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "Datadog api key"
      type: str
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    host:
      description: "Datadog host"
      type: str
    log_service:
      description: "Datadog log service"
      type: str
    log_source:
      description: "Datadog log source"
      type: str
    log_tags:
      description: "A comma-separated list of Datadog log tags formatted as 'key:value' strings"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_datadog
  gateway_log_forwarding_datadog:
    state: present

- name: Delete gateway_log_forwarding_datadog
  gateway_log_forwarding_datadog:
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
    'api_key': {'type': 'str'},
    'enable': {'type': 'str'},
    'host': {'type': 'str'},
    'log_service': {'type': 'str'},
    'log_source': {'type': 'str'},
    'log_tags': {'type': 'str'},
    'output_format': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_datadog",
        sdk_create=("GatewayUpdateLogForwardingDatadog", "gateway_update_log_forwarding_datadog"),
        sdk_update=("GatewayUpdateLogForwardingDatadog", "gateway_update_log_forwarding_datadog"),
        sdk_delete=("GatewayUpdateLogForwardingDatadog", "gateway_update_log_forwarding_datadog"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
