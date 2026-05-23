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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="gateway_log_forwarding_google_chronicle already absent")
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
        module.exit_json(changed=False, msg="gateway_log_forwarding_google_chronicle already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
