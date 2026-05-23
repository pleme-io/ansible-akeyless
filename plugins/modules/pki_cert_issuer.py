#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pki_cert_issuer
short_description: Manages a PKI certificate issuer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage pki_cert_issuer resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    allow_any_name:
      description: "If set, clients can request certificates for any CN"
      type: bool
    allow_copy_ext_from_csr:
      description: "Allow copying extra extensions from CSR"
      type: bool
    allow_subdomains:
      description: "Allow certificates for subdomains of allowed domains"
      type: bool
    allowed_domains:
      description: "Comma-delimited list of allowed domains"
      type: str
    allowed_extra_extensions:
      description: "JSON string of allowed extra extensions"
      type: str
    allowed_ip_sans:
      description: "Comma-delimited list of allowed CIDRs for IP SANs"
      type: str
    allowed_uri_sans:
      description: "Comma-delimited list of allowed URIs for URI SANs"
      type: str
    auto_renew:
      description: "Automatically renew certificates before expiration"
      type: bool
    ca_target:
      description: "Name of existing CA target (required in Public CA mode)"
      type: str
    client_flag:
      description: "Flag certificates for client auth use"
      type: bool
    code_signing_flag:
      description: "Flag certificates for code signing use"
      type: bool
    country:
      description: "Comma-separated list of countries for issued certificate"
      type: str
    create_private_crl:
      description: "Expose CRL endpoint in Gateway"
      type: bool
    create_private_ocsp:
      description: "Expose private OCSP endpoint"
      type: bool
    create_public_crl:
      description: "Expose public CRL endpoint"
      type: bool
    create_public_ocsp:
      description: "Expose public OCSP endpoint"
      type: bool
    critical_key_usage:
      description: "Mark key usage as critical"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
      type: str
    destination_path:
      description: "Destination path for generated certificates"
      type: str
    disable_wildcards:
      description: "Disable wildcard certificates"
      type: bool
    enable_acme:
      description: "Enable ACME protocol"
      type: bool
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str
    gw_cluster_url:
      description: "Gateway cluster URL"
      type: str
    is_ca:
      description: "If set, the basic constraints is-ca flag is set"
      type: bool
    key_usage:
      description: "Key usage: DigitalSignature, KeyAgreement, KeyEncipherment"
      type: str
    locality:
      description: "Locality for issued certificate"
      type: str
    max_path_len:
      description: "Maximum path length for CA certificates"
      type: int
    name:
      description: "PKI certificate issuer name"
      type: str
      required: true
    not_enforce_hostnames:
      description: "Do not enforce hostnames"
      type: bool
    not_require_cn:
      description: "Do not require common name"
      type: bool
    ocsp_ttl:
      description: "OCSP response TTL"
      type: str
    organizational_units:
      description: "Organizational units for issued certificate"
      type: str
    organizations:
      description: "Organization for issued certificate"
      type: str
    postal_code:
      description: "Postal code for issued certificate"
      type: str
    protect_certificates:
      description: "Protect generated certificates"
      type: bool
    province:
      description: "Province for issued certificate"
      type: str
    scheduled_renew:
      description: "Number of days before expiration to renew certificates"
      type: int
    server_flag:
      description: "Flag certificates for server auth use"
      type: bool
    signer_key_name:
      description: "Key to sign certificates with"
      type: str
    street_address:
      description: "Street address for issued certificate"
      type: str
    tag:
      description: "Tags for the PKI cert issuer"
      type: list
      elements: str
    ttl:
      description: "Certificate TTL"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create pki_cert_issuer
  pki_cert_issuer:
    state: present

- name: Delete pki_cert_issuer
  pki_cert_issuer:
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
    body = build_body("CreatePKICertIssuer", dict(module.params, token=token))
    return call_api(module, client, "create_pki_cert_issuer", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    #   - signer_key_name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("UpdatePKICertIssuer", dict(module.params, token=token))
    return call_api(module, client, "update_pki_cert_issuer", body)


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
        'allow_any_name': {'type': 'bool'},
        'allow_copy_ext_from_csr': {'type': 'bool'},
        'allow_subdomains': {'type': 'bool'},
        'allowed_domains': {'type': 'str'},
        'allowed_extra_extensions': {'type': 'str'},
        'allowed_ip_sans': {'type': 'str'},
        'allowed_uri_sans': {'type': 'str'},
        'auto_renew': {'type': 'bool'},
        'ca_target': {'type': 'str'},
        'client_flag': {'type': 'bool'},
        'code_signing_flag': {'type': 'bool'},
        'country': {'type': 'str'},
        'create_private_crl': {'type': 'bool'},
        'create_private_ocsp': {'type': 'bool'},
        'create_public_crl': {'type': 'bool'},
        'create_public_ocsp': {'type': 'bool'},
        'critical_key_usage': {'type': 'str'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'destination_path': {'type': 'str'},
        'disable_wildcards': {'type': 'bool'},
        'enable_acme': {'type': 'bool'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'gw_cluster_url': {'type': 'str'},
        'is_ca': {'type': 'bool'},
        'key_usage': {'type': 'str'},
        'locality': {'type': 'str'},
        'max_path_len': {'type': 'int'},
        'name': {'type': 'str', 'required': True},
        'not_enforce_hostnames': {'type': 'bool'},
        'not_require_cn': {'type': 'bool'},
        'ocsp_ttl': {'type': 'str'},
        'organizational_units': {'type': 'str'},
        'organizations': {'type': 'str'},
        'postal_code': {'type': 'str'},
        'protect_certificates': {'type': 'bool'},
        'province': {'type': 'str'},
        'scheduled_renew': {'type': 'int'},
        'server_flag': {'type': 'bool'},
        'signer_key_name': {'type': 'str'},
        'street_address': {'type': 'str'},
        'tag': {'type': 'list', 'elements': 'str'},
        'ttl': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="pki_cert_issuer already absent")
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
        module.exit_json(changed=False, msg="pki_cert_issuer already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
