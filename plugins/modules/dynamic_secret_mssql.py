#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_mssql
short_description: Manages an MSSQL dynamic secret producer
description:
  - Manage dynamic_secret_mssql resources.
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
    mssql_allowed_db_names:
      description: "CSV of allowed DB names for runtime selection when getting the secret value.
Empty => use target DB only; '*' => any DB allowed; One or more names => user must choose from this list"
      type: str
    mssql_create_statements:
      description: "MSSQL Creation statements"
      type: str
    mssql_dbname:
      description: "MSSQL database name"
      type: str
    mssql_host:
      description: "MSSQL host"
      type: str
    mssql_password:
      description: "MSSQL admin password"
      type: str
      no_log: true
    mssql_port:
      description: "MSSQL port (default: 1433)"
      type: str
    mssql_revocation_statements:
      description: "MSSQL revocation statements"
      type: str
    mssql_username:
      description: "MSSQL admin username"
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
- name: Create dynamic_secret_mssql
  dynamic_secret_mssql:
    state: present

- name: Delete dynamic_secret_mssql
  dynamic_secret_mssql:
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
        module.exit_json(changed=True, msg="dynamic_secret_mssql created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_mssql: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_mssql updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_mssql: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_mssql deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_mssql: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_mssql: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'mssql_allowed_db_names': {'type': 'str'},
        'mssql_create_statements': {'type': 'str'},
        'mssql_dbname': {'type': 'str'},
        'mssql_host': {'type': 'str'},
        'mssql_password': {'type': 'str', 'no_log': True},
        'mssql_port': {'type': 'str'},
        'mssql_revocation_statements': {'type': 'str'},
        'mssql_username': {'type': 'str'},
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
            module.exit_json(changed=False, msg="dynamic_secret_mssql already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
