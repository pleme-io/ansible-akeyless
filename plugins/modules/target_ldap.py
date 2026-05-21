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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("TargetCreateLdap", dict(module.params, token=token))
    return call_api(module, client, "target_create_ldap", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateLdap", dict(module.params, token=token))
    return call_api(module, client, "target_update_ldap", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("TargetDelete", dict(module.params, token=token))
    return call_api(module, client, "target_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("TargetGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "target_get", body, swallow_404=True)


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
        module.exit_json(changed=False, msg="target_ldap already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
