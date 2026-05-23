#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_logstash
short_description: Manages the Logstash log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_logstash resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    dns:
      description: "Logstash dns"
      type: str
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    enable_tls:
      description: "Enable tls"
      type: bool
    output_format:
      description: "Logs format [text/json]"
      type: str
    protocol:
      description: "Logstash protocol [tcp/udp]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    tls_certificate:
      description: "Logstash tls certificate"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_logstash
  gateway_log_forwarding_logstash:
    state: present

- name: Delete gateway_log_forwarding_logstash
  gateway_log_forwarding_logstash:
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
    'dns': {'type': 'str'},
    'enable': {'type': 'str'},
    'enable_tls': {'type': 'bool'},
    'output_format': {'type': 'str'},
    'protocol': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'tls_certificate': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_logstash",
        sdk_create=("GatewayUpdateLogForwardingLogstash", "gateway_update_log_forwarding_logstash"),
        sdk_update=("GatewayUpdateLogForwardingLogstash", "gateway_update_log_forwarding_logstash"),
        sdk_delete=("GatewayUpdateLogForwardingLogstash", "gateway_update_log_forwarding_logstash"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
