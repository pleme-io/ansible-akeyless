#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_ping
short_description: Manages a Ping Identity dynamic secret producer
description:
  - Manage dynamic_secret_ping resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    ping_administrative_port:
      description: "Ping Identity administrative port"
      type: str
    ping_atm_id:
      description: "Set a specific Access Token Management (ATM) instance for the created OAuth Client by providing the ATM Id. If no explicit value is given, the default pingfederate server ATM will be set."
      type: str
    ping_authorization_port:
      description: "Ping Federate authorization port"
      type: str
    ping_cert_subject_dn:
      description: "The subject DN of the client certificate. If no explicit value is given, the producer will create CA certificate and matched client certificate and return it as value. Used in conjunction with ping-issuer-dn (relevant for CLIENT_TLS_CERTIFICATE authentication method)"
      type: str
    ping_client_authentication_type:
      description: "OAuth Client Authentication Type [CLIENT_SECRET, PRIVATE_KEY_JWT, CLIENT_TLS_CERTIFICATE]"
      type: str
    ping_enforce_replay_prevention:
      description: "Determines whether PingFederate requires a unique signed JWT from the client for each action (relevant for PRIVATE_KEY_JWT authentication method) [true/false]"
      type: str
    ping_grant_types:
      description: "Ping Identity grant types"
      type: list
      elements: str
    ping_issuer_dn:
      description: "Ping Identity issuer DN"
      type: str
    ping_jwks:
      description: "Base64-encoded JSON Web Key Set (JWKS). If no explicit value is given, the producer will create JWKs and matched signed JWT (Sign Algo: RS256) and return it as value (relevant for PRIVATE_KEY_JWT authentication method)"
      type: str
    ping_jwks_url:
      description: "The URL of the JSON Web Key Set (JWKS). If no explicit value is given, the producer will create JWKs and matched signed JWT and return it as value (relevant for PRIVATE_KEY_JWT authentication method)"
      type: str
    ping_password:
      description: "Ping Identity password"
      type: str
      no_log: true
    ping_privileged_user:
      description: "Ping Identity privileged username"
      type: str
    ping_redirect_uris:
      description: "Ping Identity redirect URIs"
      type: list
      elements: str
    ping_restricted_scopes:
      description: "Limit the OAuth client to specific scopes list"
      type: list
      elements: str
    ping_signing_algo:
      description: "The signing algorithm that the client must use to sign its request objects [RS256,RS384,RS512,ES256,ES384,ES512,PS256,PS384,PS512] If no explicit value is given, the client can use any of the supported signing algorithms (relevant for PRIVATE_KEY_JWT authentication method)"
      type: str
    ping_url:
      description: "Ping Identity server URL"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
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
- name: Create dynamic_secret_ping
  dynamic_secret_ping:
    state: present

- name: Delete dynamic_secret_ping
  dynamic_secret_ping:
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
        module.exit_json(changed=True, msg="dynamic_secret_ping created")
    except Exception as e:
        module.fail_json(msg="Failed to create dynamic_secret_ping: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_ping updated")
    except Exception as e:
        module.fail_json(msg="Failed to update dynamic_secret_ping: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="dynamic_secret_ping deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete dynamic_secret_ping: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read dynamic_secret_ping: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'ping_administrative_port': {'type': 'str'},
        'ping_atm_id': {'type': 'str'},
        'ping_authorization_port': {'type': 'str'},
        'ping_cert_subject_dn': {'type': 'str'},
        'ping_client_authentication_type': {'type': 'str'},
        'ping_enforce_replay_prevention': {'type': 'str'},
        'ping_grant_types': {'type': 'list', 'elements': 'str'},
        'ping_issuer_dn': {'type': 'str'},
        'ping_jwks': {'type': 'str'},
        'ping_jwks_url': {'type': 'str'},
        'ping_password': {'type': 'str', 'no_log': True},
        'ping_privileged_user': {'type': 'str'},
        'ping_redirect_uris': {'type': 'list', 'elements': 'str'},
        'ping_restricted_scopes': {'type': 'list', 'elements': 'str'},
        'ping_signing_algo': {'type': 'str'},
        'ping_url': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
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
            module.exit_json(changed=False, msg="dynamic_secret_ping already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
