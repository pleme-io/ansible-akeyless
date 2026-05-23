#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_azure_analytics
short_description: Manages the Azure Log Analytics log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_azure_analytics resources.
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
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    workspace_id:
      description: "Azure workspace id"
      type: str
    workspace_key:
      description: "Azure workspace key"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_azure_analytics
  gateway_log_forwarding_azure_analytics:
    state: present

- name: Delete gateway_log_forwarding_azure_analytics
  gateway_log_forwarding_azure_analytics:
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
    'enable_batch': {'type': 'str'},
    'output_format': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'workspace_id': {'type': 'str'},
    'workspace_key': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_azure_analytics",
        sdk_create=("GatewayUpdateLogForwardingAzureAnalytics", "gateway_update_log_forwarding_azure_analytics"),
        sdk_update=("GatewayUpdateLogForwardingAzureAnalytics", "gateway_update_log_forwarding_azure_analytics"),
        sdk_delete=("GatewayUpdateLogForwardingAzureAnalytics", "gateway_update_log_forwarding_azure_analytics"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
