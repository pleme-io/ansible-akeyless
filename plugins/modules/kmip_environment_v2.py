#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kmip_environment_v2
short_description: Manages the singleton KMIP environment in Akeyless Vault (no update; changes force recreate)
description:
  - Manage kmip_environment_v2 resources.
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
- name: Create kmip_environment_v2
  kmip_environment_v2:
    state: present

- name: Delete kmip_environment_v2
  kmip_environment_v2:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("KmipServerSetup", dict(module.params, token=token))
    return call_api(module, client, "kmip_server_setup", body)


def update_resource(module, client, token):
    """Update not supported by the upstream API -- delete + recreate instead."""
    # WARNING: The following fields are immutable after creation.
    #   - certificate_ttl
    #   - hostname
    #   - root
    # Changing them requires destroy + recreate.

    module.fail_json(msg="kmip_environment_v2: update not supported, delete+recreate")


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("KmipDeleteServer", dict(module.params, token=token))
    return call_api(module, client, "kmip_delete_server", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("KmipDescribeServer", {"hostname": module.params.get("hostname"), "token": token})
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

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="kmip_environment_v2 already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
