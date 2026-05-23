#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dfc_key
short_description: Manages a DFC (Data File Cryptography) key
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dfc_key resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    alg:
      description: "DFC key algorithm: AES128GCM, AES256GCM, AES128SIV, AES256SIV, RSA1024, RSA2048, RSA3072, RSA4096"
      type: str
      required: true
    auto_rotate:
      description: "Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false]"
      type: str
    certificate_common_name:
      description: "Common name for generated certificate"
      type: str
    certificate_country:
      description: "Country for generated certificate"
      type: str
    certificate_digest_algo:
      description: "Digest algorithm to be used for the certificate key signing."
      type: str
    certificate_format:
      description: ""
      type: str
    certificate_locality:
      description: "Locality for generated certificate"
      type: str
    certificate_organization:
      description: "Organization for generated certificate"
      type: str
    certificate_province:
      description: "Province for generated certificate"
      type: str
    certificate_ttl:
      description: "Certificate TTL in days"
      type: int
    customer_frg_id:
      description: "The customer fragment ID that will be used to create the DFC key (if empty, the key will be created independently of a customer fragment)"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Key description"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str
    generate_self_signed_certificate:
      description: "Generate a self-signed certificate"
      type: bool
    hash_algorithm:
      description: "Specifies the hash algorithm used for the encryption key's operations, available options: [SHA256, SHA384, SHA512]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "DFCKey name"
      type: str
      required: true
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_interval:
      description: "The number of days to wait between every automatic rotation (7-365)"
      type: str
    split_level:
      description: "Number of key fragments (2-5)"
      type: int
    tag:
      description: "List of the tags attached to this DFC key"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create dfc_key
  dfc_key:
    state: present

- name: Delete dfc_key
  dfc_key:
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
    body = build_body("CreateDFCKey", dict(module.params, token=token))
    return call_api(module, client, "create_dfc_key", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - alg
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdateItem", dict(module.params, token=token))
    return call_api(module, client, "update_item", body)


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
        'alg': {'type': 'str', 'required': True},
        'auto_rotate': {'type': 'str'},
        'certificate_common_name': {'type': 'str'},
        'certificate_country': {'type': 'str'},
        'certificate_digest_algo': {'type': 'str'},
        'certificate_format': {'type': 'str'},
        'certificate_locality': {'type': 'str'},
        'certificate_organization': {'type': 'str'},
        'certificate_province': {'type': 'str'},
        'certificate_ttl': {'type': 'int'},
        'customer_frg_id': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'generate_self_signed_certificate': {'type': 'bool'},
        'hash_algorithm': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'rotation_event_in': {'type': 'list', 'elements': 'str'},
        'rotation_interval': {'type': 'str'},
        'split_level': {'type': 'int'},
        'tag': {'type': 'list', 'elements': 'str'},
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
            module.exit_json(changed=False, msg="dfc_key already absent")
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
        module.exit_json(changed=False, msg="dfc_key already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
