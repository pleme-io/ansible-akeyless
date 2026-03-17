#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_ldap
short_description: Manages an LDAP target in Akeyless Vault
description:
  - Manage target_ldap resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    bind_dn:
      description: "LDAP bind DN"
      type: str
      required: true
    bind_dn_password:
      description: "LDAP bind DN password"
      type: str
      required: true
      no_log: true
    description:
      description: "Target description"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    ldap_ca_cert:
      description: "CA Certificate File Content"
      type: str
    ldap_url:
      description: "LDAP server URL (e.g., ldap://host:389)"
      type: str
      required: true
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    server_type:
      description: "Set Ldap server type, Options:[OpenLDAP, ActiveDirectory]. Default is OpenLDAP"
      type: str
    token_expiration:
      description: "LDAP token expiration in seconds"
      type: str
'''

EXAMPLES = r'''
- name: Create target_ldap
  target_ldap:
    state: present

- name: Delete target_ldap
  target_ldap:
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
        module.exit_json(changed=True, msg="target_ldap created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_ldap: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_ldap updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_ldap: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_ldap deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_ldap: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_ldap: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'bind_dn': {'type': 'str', 'required': True},
        'bind_dn_password': {'type': 'str', 'required': True, 'no_log': True},
        'description': {'type': 'str'},
        'key': {'type': 'str'},
        'ldap_ca_cert': {'type': 'str'},
        'ldap_url': {'type': 'str', 'required': True},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'server_type': {'type': 'str'},
        'token_expiration': {'type': 'str'},
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
            module.exit_json(changed=False, msg="target_ldap already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
