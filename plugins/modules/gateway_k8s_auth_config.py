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


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="gateway_k8s_auth_config created")
    except Exception as e:
        module.fail_json(msg="Failed to create gateway_k8s_auth_config: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="gateway_k8s_auth_config updated")
    except Exception as e:
        module.fail_json(msg="Failed to update gateway_k8s_auth_config: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="gateway_k8s_auth_config deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete gateway_k8s_auth_config: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read gateway_k8s_auth_config: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'access_id': {'type': 'str', 'required': True},
        'cluster_api_type': {'type': 'str'},
        'disable_issuer_validation': {'type': 'str'},
        'k8s_auth_type': {'type': 'str'},
        'k8s_ca_cert': {'type': 'str'},
        'k8s_client_certificate': {'type': 'str'},
        'k8s_client_key': {'type': 'str'},
        'k8s_host': {'type': 'str', 'required': True},
        'k8s_issuer': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'rancher_api_key': {'type': 'str'},
        'rancher_cluster_id': {'type': 'str'},
        'signing_key': {'type': 'str', 'required': True},
        'token_exp': {'type': 'int'},
        'token_reviewer_jwt': {'type': 'str'},
        'use_gw_service_account': {'type': 'bool'},
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
            module.exit_json(changed=False, msg="gateway_k8s_auth_config already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
