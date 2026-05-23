#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_google_chronicle
short_description: Manages the Google Chronicle log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

argument_spec = {
    'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
    'customer_id': {'type': 'str'},
    'enable': {'type': 'str'},
    'gcp_key': {'type': 'str', 'no_log': True},
    'log_type': {'type': 'str'},
    'output_format': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'region': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='gateway_log_forwarding_google_chronicle',
        sdk_create=('GatewayUpdateLogForwardingGoogleChronicle', 'gateway_update_log_forwarding_google_chronicle'),
        sdk_update=('GatewayUpdateLogForwardingGoogleChronicle', 'gateway_update_log_forwarding_google_chronicle'),
        sdk_delete=('GatewayUpdateLogForwardingGoogleChronicle', 'gateway_update_log_forwarding_google_chronicle'),
        sdk_read=('GatewayGetLogForwarding', 'gateway_get_log_forwarding'),
    )


if __name__ == '__main__':
    main()
