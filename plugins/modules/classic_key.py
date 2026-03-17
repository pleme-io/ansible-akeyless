#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: classic_key
short_description: Manages a classic cryptographic key
description:
  - Manage classic_key resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    alg:
      description: "Classic key algorithm: AES128GCM, AES256GCM, AES128SIV, AES256SIV, RSA1024, RSA2048, RSA3072, RSA4096, EC256, EC384"
      type: str
      required: true
    auto_rotate:
      description: "Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false]"
      type: str
    cert_file_data:
      description: "Certificate PEM data (for RSA keys)"
      type: str
      no_log: true
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
    gpg_alg:
      description: "gpg alg: Relevant only if GPG key type selected; options: [RSA1024, RSA2048, RSA3072, RSA4096, Ed25519]"
      type: str
    hash_algorithm:
      description: "Specifies the hash algorithm used for the encryption key's operations, available options: [SHA256, SHA384, SHA512]"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key_data:
      description: "Key material (base64 encoded)"
      type: str
      no_log: true
    name:
      description: "ClassicKey name"
      type: str
      required: true
    protection_key_name:
      description: "Encryption key used to protect this key"
      type: str
    rotation_event_in:
      description: "How many days before the rotation of the item would you like to be notified"
      type: list
      elements: str
    rotation_interval:
      description: "The number of days to wait between every automatic rotation (1-365)"
      type: str
    tags:
      description: "Tags for the key"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create classic_key
  classic_key:
    state: present

- name: Delete classic_key
  classic_key:
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
        module.exit_json(changed=True, msg="classic_key created")
    except Exception as e:
        module.fail_json(msg="Failed to create classic_key: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - alg
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="classic_key updated")
    except Exception as e:
        module.fail_json(msg="Failed to update classic_key: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="classic_key deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete classic_key: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read classic_key: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'alg': {'type': 'str', 'required': True},
        'auto_rotate': {'type': 'str'},
        'cert_file_data': {'type': 'str', 'no_log': True},
        'certificate_common_name': {'type': 'str'},
        'certificate_country': {'type': 'str'},
        'certificate_digest_algo': {'type': 'str'},
        'certificate_format': {'type': 'str'},
        'certificate_locality': {'type': 'str'},
        'certificate_organization': {'type': 'str'},
        'certificate_province': {'type': 'str'},
        'certificate_ttl': {'type': 'int'},
        'delete_protection': {'type': 'bool'},
        'description': {'type': 'str'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'generate_self_signed_certificate': {'type': 'bool'},
        'gpg_alg': {'type': 'str'},
        'hash_algorithm': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'key_data': {'type': 'str', 'no_log': True},
        'name': {'type': 'str', 'required': True},
        'protection_key_name': {'type': 'str'},
        'rotation_event_in': {'type': 'list', 'elements': 'str'},
        'rotation_interval': {'type': 'str'},
        'tags': {'type': 'list', 'elements': 'str'},
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
            module.exit_json(changed=False, msg="classic_key already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
