#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_ping
short_description: Manages a Ping Identity gateway producer (deprecated; prefer akeyless_dynamic_secret_ping)
description:
  - Manage gateway_producer_ping resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    ping_administrative_port:
      description: "Ping Federate administrative port"
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
      description: "List of OAuth client grant types [IMPLICIT, AUTHORIZATION_CODE, CLIENT_CREDENTIALS, TOKEN_EXCHANGE, REFRESH_TOKEN, ASSERTION_GRANTS, PASSWORD, RESOURCE_OWNER_CREDENTIALS]. If no explicit value is given, AUTHORIZATION_CODE will be selected as default."
      type: list
      elements: str
    ping_issuer_dn:
      description: "Issuer DN of trusted CA certificate that imported into Ping Federate server. You may select \'Trust Any\' to trust all the existing issuers in Ping Federate server. Used in conjunction with ping-cert-subject-dn (relevant for CLIENT_TLS_CERTIFICATE authentication method)"
      type: str
    ping_jwks:
      description: "Base64-encoded JSON Web Key Set (JWKS). If no explicit value is given, the producer will create JWKs and matched signed JWT (Sign Algo: RS256) and return it as value (relevant for PRIVATE_KEY_JWT authentication method)"
      type: str
    ping_jwks_url:
      description: "The URL of the JSON Web Key Set (JWKS). If no explicit value is given, the producer will create JWKs and matched signed JWT and return it as value (relevant for PRIVATE_KEY_JWT authentication method)"
      type: str
    ping_password:
      description: "Ping Federate privileged user password"
      type: str
    ping_privileged_user:
      description: "Ping Federate privileged user"
      type: str
    ping_redirect_uris:
      description: "List of URIs to which the OAuth authorization server may redirect the resource owner's user agent after authorization is obtained. At least one redirection URI is required for the AUTHORIZATION_CODE and IMPLICIT grant types."
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
      description: "Ping URL"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "The time from dynamic secret creation to expiration."
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_ping
  gateway_producer_ping:
    state: present

- name: Delete gateway_producer_ping
  gateway_producer_ping:
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
    body = build_body("GatewayCreateProducerPing", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_ping", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerPing", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_ping", body)


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
        'delete_protection': {'type': 'str'},
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
        'ping_password': {'type': 'str'},
        'ping_privileged_user': {'type': 'str'},
        'ping_redirect_uris': {'type': 'list', 'elements': 'str'},
        'ping_restricted_scopes': {'type': 'list', 'elements': 'str'},
        'ping_signing_algo': {'type': 'str'},
        'ping_url': {'type': 'str'},
        'producer_encryption_key_name': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
        'target_name': {'type': 'str'},
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
        module.exit_json(changed=False, msg="gateway_producer_ping already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
