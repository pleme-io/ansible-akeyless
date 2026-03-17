#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_rdp
short_description: Manages an RDP dynamic secret producer
description:
  - Manage dynamic_secret_rdp resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    allow_user_extend_session:
      description: "AllowUserExtendSession"
      type: int
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (relevant only for fixed-user-only=true)"
      type: str
    fixed_user_only:
      description: "Allow access using externally (IdP) provided username [true/false]"
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
    rdp_admin_name:
      description: "RDP admin username"
      type: str
    rdp_admin_pwd:
      description: "RDP admin password"
      type: str
      no_log: true
    rdp_host_name:
      description: "RDP host address"
      type: str
    rdp_host_port:
      description: "RDP port (default: 3389)"
      type: str
    rdp_user_groups:
      description: "RDP user groups for dynamic users"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    secure_access_rd_gateway_server:
      description: "RD Gateway server"
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
    warn_user_before_expiration:
      description: "WarnBeforeUserExpiration"
      type: int
'''

EXAMPLES = r'''
- name: Create dynamic_secret_rdp
  dynamic_secret_rdp:
    state: present

- name: Delete dynamic_secret_rdp
  dynamic_secret_rdp:
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
        module.exit_json(changed=True, msg="dynamic_secret_rdp created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_rdp: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_rdp updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_rdp: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_rdp deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_rdp: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_rdp: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'allow_user_extend_session': {'type': 'int'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str'},
        'fixed_user_only': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'rdp_admin_name': {'type': 'str'},
        'rdp_admin_pwd': {'type': 'str', 'no_log': True},
        'rdp_host_name': {'type': 'str'},
        'rdp_host_port': {'type': 'str'},
        'rdp_user_groups': {'type': 'str'},
        'secure_access_delay': {'type': 'int'},
        'secure_access_rd_gateway_server': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'user_ttl': {'type': 'str'},
        'warn_user_before_expiration': {'type': 'int'},
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
            module.exit_json(changed=False, msg="dynamic_secret_rdp already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
