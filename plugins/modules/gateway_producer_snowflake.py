#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_snowflake
short_description: Manages a Snowflake gateway producer (deprecated; prefer akeyless_dynamic_secret_snowflake)
description:
  - Manage gateway_producer_snowflake resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    account:
      description: "Account name"
      type: str
    account_password:
      description: "Database Password"
      type: str
    account_username:
      description: "Database Username"
      type: str
    auth_mode:
      description: "The authentication mode for the temporary user [password/key]"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    db_name:
      description: "Database name"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key_algo:
      description: ""
      type: str
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    private_key:
      description: "RSA Private key (base64 encoded)"
      type: str
    private_key_passphrase:
      description: "The Private key passphrase"
      type: str
    role:
      description: "User role"
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
    warehouse:
      description: "Warehouse name"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_snowflake
  gateway_producer_snowflake:
    state: present

- name: Delete gateway_producer_snowflake
  gateway_producer_snowflake:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayCreateProducerSnowflake", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_snowflake", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerSnowflake", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_snowflake", body)


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
        'account': {'type': 'str', 'required': True},
        'account_password': {'type': 'str'},
        'account_username': {'type': 'str', 'required': True},
        'auth_mode': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'db_name': {'type': 'str', 'required': True},
        'delete_protection': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'key_algo': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'private_key': {'type': 'str', 'required': True},
        'private_key_passphrase': {'type': 'str'},
        'role': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'user_ttl': {'type': 'str'},
        'warehouse': {'type': 'str'},
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
        module.exit_json(changed=False, msg="gateway_producer_snowflake already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
