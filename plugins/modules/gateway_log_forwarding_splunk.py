#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_splunk
short_description: Manages the Splunk log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_splunk",
        sdk_create=("GatewayUpdateLogForwardingSplunk", "gateway_update_log_forwarding_splunk"),
        sdk_update=("GatewayUpdateLogForwardingSplunk", "gateway_update_log_forwarding_splunk"),
        sdk_delete=("GatewayUpdateLogForwardingSplunk", "gateway_update_log_forwarding_splunk"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
