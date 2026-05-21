#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_rabbitmq
short_description: Manages a RabbitMQ dynamic secret producer
description:
  - Manage dynamic_secret_rabbitmq resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
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
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    rabbitmq_admin_pwd:
      description: "RabbitMQ Admin password"
      type: str
    rabbitmq_admin_user:
      description: "RabbitMQ Admin User"
      type: str
    rabbitmq_server_uri:
      description: "RabbitMQ management API URI"
      type: str
    rabbitmq_user_conf_permission:
      description: "RabbitMQ configure permission for dynamic users"
      type: str
    rabbitmq_user_read_permission:
      description: "RabbitMQ read permission for dynamic users"
      type: str
    rabbitmq_user_tags:
      description: "RabbitMQ tags for dynamic users (comma-separated)"
      type: str
    rabbitmq_user_vhost:
      description: "RabbitMQ vhost for dynamic users"
      type: str
    rabbitmq_user_write_permission:
      description: "RabbitMQ write permission for dynamic users"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_rabbitmq
  dynamic_secret_rabbitmq:
    state: present

- name: Delete dynamic_secret_rabbitmq
  dynamic_secret_rabbitmq:
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
    body = build_body("DynamicSecretCreateRabbitMq", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_create_rabbit_mq", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("DynamicSecretUpdateRabbitMq", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_update_rabbit_mq", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DynamicSecretDelete", dict(module.params, token=token))
    return call_api(module, client, "dynamic_secret_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DynamicSecretGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "dynamic_secret_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'rabbitmq_admin_pwd': {'type': 'str'},
        'rabbitmq_admin_user': {'type': 'str'},
        'rabbitmq_server_uri': {'type': 'str'},
        'rabbitmq_user_conf_permission': {'type': 'str'},
        'rabbitmq_user_read_permission': {'type': 'str'},
        'rabbitmq_user_tags': {'type': 'str'},
        'rabbitmq_user_vhost': {'type': 'str'},
        'rabbitmq_user_write_permission': {'type': 'str'},
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

    if module.check_mode:
        changed = (current is None and state == 'present') or (current is not None and state == 'absent')
        module.exit_json(changed=changed)

    if state == 'absent':
        if current is not None:
            result = delete_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        module.exit_json(changed=False, msg="dynamic_secret_rabbitmq already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
