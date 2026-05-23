#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kmip_environment
short_description: Manages a KMIP environment in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage kmip_environment resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_ttl:
      description: "Server certificate TTL in days"
      type: int
    hostname:
      description: "Hostname"
      type: str
      required: true
    root:
      description: "Root path of KMIP Resources"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create kmip_environment
  kmip_environment:
    state: present

- name: Delete kmip_environment
  kmip_environment:
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
    body = build_body("KmipServerSetup", dict(module.params, token=token))
    return call_api(module, client, "kmip_server_setup", body)


def update_resource(module, client, token):
    """Update not supported by the upstream API -- delete + recreate instead."""
    module.fail_json(msg="kmip_environment: update not supported, delete+recreate")


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("KmipDeleteServer", dict(module.params, token=token))
    return call_api(module, client, "kmip_delete_server", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("KmipDescribeServer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "kmip_describe_server", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'certificate_ttl': {'type': 'int'},
        'hostname': {'type': 'str', 'required': True},
        'root': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="kmip_environment already absent")
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
        module.exit_json(changed=False, msg="kmip_environment already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
