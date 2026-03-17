#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_allowed_access
short_description: Manages gateway allowed access in Akeyless
description:
  - Manage gateway_allowed_access resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    SubClaimsCaseInsensitive:
      description: ""
      type: bool
    access_id:
      description: "The access ID to attach to this allowed access"
      type: str
      required: true
    case_sensitive:
      description: "Treat sub claims as case-sensitive [true/false]"
      type: str
    description:
      description: "Allowed access description"
      type: str
    name:
      description: "Allowed access name"
      type: str
      required: true
    permissions:
      description: "Comma-separated list of permissions: defaults, targets, classic_keys, automatic_migration, ldap_auth, dynamic_secret, k8s_auth, log_forwarding, zero_knowledge_encryption, rotated_secret, caching, event_forwarding, admin, kmip, general, rotate_secret_value"
      type: str
    sub_claims:
      description: "Key/val of sub claims, e.g. group=admins,developers"
      type: dict
'''

EXAMPLES = r'''
- name: Create gateway_allowed_access
  gateway_allowed_access:
    state: present

- name: Delete gateway_allowed_access
  gateway_allowed_access:
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
        module.exit_json(changed=True, msg="gateway_allowed_access created")
    except Exception as e:
        module.fail_json(msg="Failed to create gateway_allowed_access: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="gateway_allowed_access updated")
    except Exception as e:
        module.fail_json(msg="Failed to update gateway_allowed_access: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="gateway_allowed_access deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete gateway_allowed_access: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read gateway_allowed_access: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'SubClaimsCaseInsensitive': {'type': 'bool'},
        'access_id': {'type': 'str', 'required': True},
        'case_sensitive': {'type': 'str'},
        'description': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'permissions': {'type': 'str'},
        'sub_claims': {'type': 'dict'},
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
            module.exit_json(changed=False, msg="gateway_allowed_access already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
