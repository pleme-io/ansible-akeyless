#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_gcp
short_description: Manages a GCP gateway producer (deprecated; prefer akeyless_dynamic_secret_gcp)
description:
  - Manage gateway_producer_gcp resources.
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
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    fixed_user_claim_keyname:
      description: "For externally provided users, denotes the key-name of IdP claim to extract the username from (Relevant only when --access-type=external)"
      type: str
    gcp_cred_type:
      description: ""
      type: str
    gcp_key:
      description: "Base64-encoded service account private key text"
      type: str
    gcp_key_algo:
      description: "Service account key algorithm, e.g. KEY_ALG_RSA_1024 (Relevant only when --access-type=sa and --gcp-cred-type=key)"
      type: str
    gcp_project_id:
      description: "GCP Project ID override for dynamic secret operations"
      type: str
    gcp_sa_email:
      description: "The email of the fixed service account to generate keys or tokens for (Relevant only when --access-type=sa and --service-account-type=fixed)"
      type: str
    gcp_token_scopes:
      description: "Access token scopes list, e.g. scope1,scope2 (Relevant only when --access-type=sa; required when --gcp-cred-type=token)"
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
      description: "Role binding definitions in JSON format (Relevant only when --access-type=sa and --service-account-type=dynamic)"
      type: str
    role_names:
      description: "Comma-separated list of GCP roles to assign to the user (Relevant only when --access-type=external)"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    service_account_type:
      description: "The type of the GCP service account. Options [fixed, dynamic] (Relevant only when --access-type=sa)"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_gcp
  gateway_producer_gcp:
    state: present

- name: Delete gateway_producer_gcp
  gateway_producer_gcp:
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
    body = build_body("GatewayCreateProducerGcp", dict(module.params, token=token))
    return call_api(module, client, "gateway_create_producer_gcp", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateProducerGcp", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_producer_gcp", body)


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
        'access_type': {'type': 'str'},
        'custom_username_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
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

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="gateway_producer_gcp already absent")
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
        module.exit_json(changed=False, msg="gateway_producer_gcp already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
