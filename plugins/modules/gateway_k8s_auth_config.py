#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_k8s_auth_config
short_description: Manages a gateway Kubernetes auth config in Akeyless
description:
  - Manage gateway_k8s_auth_config resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_id:
      description: "The access ID of the Kubernetes auth method"
      type: str
      required: true
    cluster_api_type:
      description: "Cluster access type. options: [native_k8s, rancher]"
      type: str
    disable_issuer_validation:
      description: "Disable issuer validation [true/false]"
      type: str
    k8s_auth_type:
      description: "K8S auth type [token/certificate]. (relevant for 'native_k8s' only)"
      type: str
    k8s_ca_cert:
      description: "The CA Certificate (base64 encoded) to use to call into the kubernetes API server"
      type: str
    k8s_client_certificate:
      description: "Content of the k8 client certificate (PEM format) in a Base64 format (relevant for 'native_k8s' only)"
      type: str
    k8s_client_key:
      description: "Content of the k8 client private key (PEM format) in a Base64 format (relevant for 'native_k8s' only)"
      type: str
    k8s_host:
      description: "The URL of the kubernetes API server"
      type: str
      required: true
    k8s_issuer:
      description: "The Kubernetes JWT issuer name. K8SIssuer is the claim that specifies who issued the Kubernetes token"
      type: str
    name:
      description: "K8S Auth config name"
      type: str
      required: true
    rancher_api_key:
      description: "The api key used to access the TokenReview API to validate other JWTs (relevant for 'rancher' only)"
      type: str
    rancher_cluster_id:
      description: "The cluster id as define in rancher (relevant for 'rancher' only)"
      type: str
    signing_key:
      description: "The private key (base64 encoded) associated with the public key defined in the Kubernetes auth"
      type: str
      required: true
    token_exp:
      description: "Time in seconds of expiration of the Akeyless Kube Auth Method token"
      type: int
    token_reviewer_jwt:
      description: "A Kubernetes service account JWT used to access the TokenReview API to validate other JWTs (relevant for 'native_k8s' only).
If not set, the JWT submitted in the authentication process will be used to access the Kubernetes TokenReview API."
      type: str
    use_gw_service_account:
      description: "Use the GW's service account"
      type: bool
'''

EXAMPLES = r'''
- name: Create gateway_k8s_auth_config
  gateway_k8s_auth_config:
    state: present

- name: Delete gateway_k8s_auth_config
  gateway_k8s_auth_config:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayCreateK8SAuthConfig", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_k8_s_auth_config", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateK8SAuthConfig", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_k8_s_auth_config", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayDeleteK8SAuthConfig", dict(module.params, token=token))
    return call_api(module, client, "gateway_delete_k8_s_auth_config", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetK8SAuthConfig", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_k8_s_auth_config", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'access_id': {'type': 'str', 'required': True},
        'cluster_api_type': {'type': 'str'},
        'disable_issuer_validation': {'type': 'str'},
        'k8s_auth_type': {'type': 'str'},
        'k8s_ca_cert': {'type': 'str', 'required': True},
        'k8s_client_certificate': {'type': 'str'},
        'k8s_client_key': {'type': 'str'},
        'k8s_host': {'type': 'str', 'required': True},
        'k8s_issuer': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'rancher_api_key': {'type': 'str'},
        'rancher_cluster_id': {'type': 'str'},
        'signing_key': {'type': 'str', 'required': True},
        'token_exp': {'type': 'int'},
        'token_reviewer_jwt': {'type': 'str', 'required': True},
        'use_gw_service_account': {'type': 'bool'},
        'gateway_url': {'type': 'str'},
        # NOTE: no auth-side `access_id` here -- the resource field above
        # shadows it. Auth `access_id` comes from AKEYLESS_ACCESS_ID env.
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

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="gateway_k8s_auth_config already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        result = delete_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # state == 'present'
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = create_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs
    # from what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False, msg="gateway_k8s_auth_config already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
