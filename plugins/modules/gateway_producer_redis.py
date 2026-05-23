#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_redis
short_description: Manages a Redis gateway producer (deprecated; prefer akeyless_dynamic_secret_redis)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_redis resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present

    acl_rules:
      description: "A JSON array list of redis ACL rules to attach to the created user. For available rules see the ACL CAT command https://redis.io/commands/acl-cat
      type: str
By default the user will have permissions to read all keys '['~*', '+@read']'"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    host:
      description: "Redis Host"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    port:
      description: "Redis Port"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    ssl:
      description: "Enable/Disable SSL [true/false]"
      type: bool
    ssl_certificate:
      description: "SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA)"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_redis
  gateway_producer_redis:
    state: present

- name: Delete gateway_producer_redis
  gateway_producer_redis:
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
    body = build_body("GatewayCreateProducerRedis", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_redis", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerRedis", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_redis", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'acl_rules': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'host': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str', 'no_log': False},
        'port': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'ssl': {'type': 'bool'},
        'ssl_certificate': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'user_ttl': {'type': 'str'},
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
            module.exit_json(changed=False, msg="gateway_producer_redis already absent")
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
        module.exit_json(changed=False, msg="gateway_producer_redis already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
