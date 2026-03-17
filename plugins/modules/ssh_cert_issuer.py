#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ssh_cert_issuer
short_description: Manages an SSH certificate issuer
description:
  - Manage ssh_cert_issuer resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    ProviderType:
      description: ""
      type: str
    allowed_users:
      description: "Users allowed to fetch the certificate, e.g. root,ubuntu"
      type: str
      required: true
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    extensions:
      description: "Signed certificates with extensions, e.g. permit-port-forwarding"
      type: dict
    external_username:
      description: "Externally provided username [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "Key-name of IdP claim to extract username from (for external-username=true)"
      type: str
    host_provider:
      description: "Host provider type [explicit/target]"
      type: str
    name:
      description: "SSH certificate issuer name"
      type: str
      required: true
    principals:
      description: "Signed certificates with principal, e.g. example_role1,example_role2"
      type: str
    secure_access_use_internal_ssh_access:
      description: "Use internal SSH Access"
      type: bool
    signer_key_name:
      description: "Key to sign the certificate with"
      type: str
      required: true
    tag:
      description: "Tags for the SSH cert issuer"
      type: list
      elements: str
    target:
      description: "A list of linked targets to be associated, Relevant only for Secure Remote Access for ssh cert issuer, ldap rotated secret and ldap dynamic secret, To specify multiple targets use argument multiple times"
      type: list
      elements: str
    ttl:
      description: "Certificate TTL in seconds"
      type: int
      required: true
'''

EXAMPLES = r'''
- name: Create ssh_cert_issuer
  ssh_cert_issuer:
    state: present

- name: Delete ssh_cert_issuer
  ssh_cert_issuer:
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
        module.exit_json(changed=True, msg="ssh_cert_issuer created")
    except Exception as e:
        module.fail_json(msg="Failed to create ssh_cert_issuer: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    #   - signer_key_name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="ssh_cert_issuer updated")
    except Exception as e:
        module.fail_json(msg="Failed to update ssh_cert_issuer: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="ssh_cert_issuer deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete ssh_cert_issuer: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read ssh_cert_issuer: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'ProviderType': {'type': 'str'},
        'allowed_users': {'type': 'str', 'required': True},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'extensions': {'type': 'dict'},
        'external_username': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str'},
        'host_provider': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'principals': {'type': 'str'},
        'secure_access_use_internal_ssh_access': {'type': 'bool'},
        'signer_key_name': {'type': 'str', 'required': True},
        'tag': {'type': 'list', 'elements': 'str'},
        'target': {'type': 'list', 'elements': 'str'},
        'ttl': {'type': 'int', 'required': True},
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
            module.exit_json(changed=False, msg="ssh_cert_issuer already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
