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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("CreateSSHCertIssuer", dict(module.params, token=token))
    return call_api(module, client, "create_ssh_cert_issuer", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    #   - signer_key_name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdateSSHCertIssuer", dict(module.params, token=token))
    return call_api(module, client, "update_ssh_cert_issuer", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("DeleteItem", dict(module.params, token=token))
    return call_api(module, client, "delete_item", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("DescribeItem", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "describe_item", body, swallow_404=True)


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
        module.exit_json(changed=False, msg="ssh_cert_issuer already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
