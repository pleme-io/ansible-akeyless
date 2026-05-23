#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_logz_io
short_description: Manages the Logz.io log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_logz_io resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    logz_io_token:
      description: "Logz-io token"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    protocol:
      description: "LogzIo protocol [tcp/https]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_logz_io
  gateway_log_forwarding_logz_io:
    state: present

- name: Delete gateway_log_forwarding_logz_io
  gateway_log_forwarding_logz_io:
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
    'logz_io_token': {'type': 'str', 'no_log': True},
    'output_format': {'type': 'str'},
    'protocol': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='gateway_log_forwarding_logz_io',
        sdk_create=('GatewayUpdateLogForwardingLogzIo', 'gateway_update_log_forwarding_logz_io'),
        sdk_update=('GatewayUpdateLogForwardingLogzIo', 'gateway_update_log_forwarding_logz_io'),
        sdk_delete=('GatewayUpdateLogForwardingLogzIo', 'gateway_update_log_forwarding_logz_io'),
        sdk_read=('GatewayGetLogForwarding', 'gateway_get_log_forwarding'),
    )


if __name__ == '__main__':
    main()
