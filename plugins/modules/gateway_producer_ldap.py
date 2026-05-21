#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_ldap
short_description: Manages an LDAP gateway producer (deprecated; prefer akeyless_dynamic_secret_ldap)
description:
  - Manage gateway_producer_ldap resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    ProviderType:
      description: ""
      type: str
    bind_dn:
      description: "Bind DN"
      type: str
    bind_dn_password:
      description: "Bind DN Password"
      type: str
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    external_username:
      description: "Externally provided username [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (relevant only for external-username=true)"
      type: str
    group_dn:
      description: "Group DN which the temporary user should be added"
      type: str
    host_provider:
      description: "Host provider type [explicit/target], Default Host provider is explicit, Relevant only for Secure Remote Access of ssh cert issuer, ldap rotated secret and ldap dynamic secret"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    ldap_ca_cert:
      description: "CA Certificate File Content"
      type: str
    ldap_url:
      description: "LDAP Server URL"
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
    secure_access_rd_gateway_server:
      description: "RD Gateway server"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target:
      description: "A list of linked targets to be associated, Relevant only for Secure Remote Access for ssh cert issuer, ldap rotated secret and ldap dynamic secret, To specify multiple targets use argument multiple times"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    token_expiration:
      description: "Token expiration"
      type: str
    user_attribute:
      description: "User Attribute"
      type: str
    user_dn:
      description: "User DN"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_ldap
  gateway_producer_ldap:
    state: present

- name: Delete gateway_producer_ldap
  gateway_producer_ldap:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayCreateProducerLdap", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_ldap", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerLdap", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_ldap", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteProducer", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_producer", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetProducer", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_producer", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'ProviderType': {'type': 'str'},
        'bind_dn': {'type': 'str'},
        'bind_dn_password': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'external_username': {'type': 'str'},
        'fixed_user_claim_keyname': {'type': 'str'},
        'group_dn': {'type': 'str'},
        'host_provider': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'ldap_ca_cert': {'type': 'str'},
        'ldap_url': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'password_length': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'secure_access_delay': {'type': 'int'},
        'secure_access_rd_gateway_server': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
        'token_expiration': {'type': 'str'},
        'user_attribute': {'type': 'str'},
        'user_dn': {'type': 'str'},
        'user_ttl': {'type': 'str'},
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
        module.exit_json(changed=False, msg="gateway_producer_ldap already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
