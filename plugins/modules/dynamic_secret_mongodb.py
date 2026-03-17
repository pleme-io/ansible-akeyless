#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_mongodb
short_description: Manages a MongoDB dynamic secret producer
description:
  - Manage dynamic_secret_mongodb resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    mongodb_atlas_api_private_key:
      description: "MongoDB Atlas API private key"
      type: str
      no_log: true
    mongodb_atlas_api_public_key:
      description: "MongoDB Atlas API public key"
      type: str
    mongodb_atlas_project_id:
      description: "MongoDB Atlas project ID"
      type: str
    mongodb_custom_data:
      description: "MongoDB custom data"
      type: str
    mongodb_default_auth_db:
      description: "MongoDB default authentication database"
      type: str
    mongodb_host_port:
      description: "MongoDB host:port"
      type: str
    mongodb_name:
      description: "MongoDB database name"
      type: str
    mongodb_password:
      description: "MongoDB admin password"
      type: str
      no_log: true
    mongodb_roles:
      description: "MongoDB roles (e.g., readWrite@db)"
      type: str
    mongodb_scopes:
      description: "MongoDB Scopes (Atlas only)"
      type: str
    mongodb_server_uri:
      description: "MongoDB server URI"
      type: str
    mongodb_uri_options:
      description: "MongoDB URI options"
      type: str
    mongodb_username:
      description: "MongoDB admin username"
      type: str
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
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
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
- name: Create dynamic_secret_mongodb
  dynamic_secret_mongodb:
    state: present

- name: Delete dynamic_secret_mongodb
  dynamic_secret_mongodb:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_mongodb created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_mongodb: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_mongodb updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_mongodb: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_mongodb deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_mongodb: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_mongodb: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'mongodb_atlas_api_private_key': {'type': 'str', 'no_log': True},
        'mongodb_atlas_api_public_key': {'type': 'str'},
        'mongodb_atlas_project_id': {'type': 'str'},
        'mongodb_custom_data': {'type': 'str'},
        'mongodb_default_auth_db': {'type': 'str'},
        'mongodb_host_port': {'type': 'str'},
        'mongodb_name': {'type': 'str'},
        'mongodb_password': {'type': 'str', 'no_log': True},
        'mongodb_roles': {'type': 'str'},
        'mongodb_scopes': {'type': 'str'},
        'mongodb_server_uri': {'type': 'str'},
        'mongodb_uri_options': {'type': 'str'},
        'mongodb_username': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'secure_access_delay': {'type': 'int'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'user_ttl': {'type': 'str'},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params.get('state', 'present')
    current = read_resource(module)

    if module.check_mode:
        module.exit_json(changed=(current is None and state == 'present')
                         or (current is not None and state == 'absent'))

    if state == 'absent':
        if current is not None:
            delete_resource(module)
        else:
            module.exit_json(changed=False, msg="dynamic_secret_mongodb already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
