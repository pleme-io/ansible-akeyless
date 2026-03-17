#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_salesforce
short_description: Manages a Salesforce target in Akeyless Vault
description:
  - Manage target_salesforce resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    app_private_key_data:
      description: "Base64 encoded PEM of the connected app private key (relevant for JWT auth only)"
      type: str
    auth_flow:
      description: "Salesforce auth flow: user-password or jwt-bearer"
      type: str
      required: true
    ca_cert_data:
      description: "Base64 encoded PEM cert to use when uploading a new key to Salesforce"
      type: str
    ca_cert_name:
      description: "name of the certificate in Salesforce tenant to use when uploading new key"
      type: str
    client_id:
      description: "Salesforce connected app client ID"
      type: str
      required: true
    client_secret:
      description: "Salesforce connected app client secret"
      type: str
      no_log: true
    description:
      description: "Target description"
      type: str
    email:
      description: "The email of the user attached to the oauth2 app used for connecting to Salesforce"
      type: str
      required: true
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    security_token:
      description: "Salesforce security token"
      type: str
      no_log: true
    tenant_url:
      description: "Salesforce tenant URL"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create target_salesforce
  target_salesforce:
    state: present

- name: Delete target_salesforce
  target_salesforce:
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
        module.exit_json(changed=True, msg="target_salesforce created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_salesforce: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_salesforce updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_salesforce: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_salesforce deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_salesforce: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_salesforce: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'app_private_key_data': {'type': 'str'},
        'auth_flow': {'type': 'str', 'required': True},
        'ca_cert_data': {'type': 'str'},
        'ca_cert_name': {'type': 'str'},
        'client_id': {'type': 'str', 'required': True},
        'client_secret': {'type': 'str', 'no_log': True},
        'description': {'type': 'str'},
        'email': {'type': 'str', 'required': True},
        'key': {'type': 'str'},
        'max_versions': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'security_token': {'type': 'str', 'no_log': True},
        'tenant_url': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="target_salesforce already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
