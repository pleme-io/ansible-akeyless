#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_gcp
short_description: Manages a GCP dynamic secret producer
description:
  - Manage dynamic_secret_gcp resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_type:
      description: ""
      type: str
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
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (Relevant only when --access-type=external)"
      type: str
    gcp_cred_type:
      description: "GCP credential type: token or key"
      type: str
    gcp_key:
      description: "Base64-encoded service account private key text"
      type: str
    gcp_key_algo:
      description: "GCP service account key algorithm"
      type: str
    gcp_project_id:
      description: "GCP Project ID override for dynamic secret operations"
      type: str
    gcp_sa_email:
      description: "GCP service account email"
      type: str
    gcp_token_scopes:
      description: "GCP access token scopes (comma-separated)"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    role_binding:
      description: "Role binding in the format Role,Resource"
      type: str
    role_names:
      description: "Comma-separated list of GCP roles to assign to the user (Relevant only when --access-type=external)"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    service_account_type:
      description: "Service account type: fixed or dynamic"
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
- name: Create dynamic_secret_gcp
  dynamic_secret_gcp:
    state: present

- name: Delete dynamic_secret_gcp
  dynamic_secret_gcp:
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
        module.exit_json(changed=True, msg="dynamic_secret_gcp created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_gcp: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_gcp updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_gcp: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_gcp deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_gcp: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_gcp: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'access_type': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str'},
        'gcp_cred_type': {'type': 'str'},
        'gcp_key': {'type': 'str'},
        'gcp_key_algo': {'type': 'str'},
        'gcp_project_id': {'type': 'str'},
        'gcp_sa_email': {'type': 'str'},
        'gcp_token_scopes': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'producer_encryption_key_name': {'type': 'str'},
        'role_binding': {'type': 'str'},
        'role_names': {'type': 'str'},
        'secure_access_delay': {'type': 'int'},
        'service_account_type': {'type': 'str'},
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
            module.exit_json(changed=False, msg="dynamic_secret_gcp already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
