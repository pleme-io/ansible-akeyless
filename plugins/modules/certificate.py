#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: certificate
short_description: Manages a certificate in Akeyless Vault
description:
  - Manage certificate resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_data:
      description: "Content of the certificate in a Base64 format."
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Description of the object"
      type: str
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str
    format:
      description: "CertificateFormat of the certificate and private key, possible values: cer,crt,pem,pfx,p12.
Required when passing inline certificate content with --certificate-data or --key-data, otherwise format is derived from the file extension."
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    key:
      description: "The name of a key to use to encrypt the certificate's key (if empty, the
account default protectionKey key will be used)"
      type: str
    key_data:
      description: "Content of the certificate's private key in a Base64 format."
      type: str
    name:
      description: "Certificate name"
      type: str
      required: true
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
'''

EXAMPLES = r'''
- name: Create certificate
  certificate:
    state: present

- name: Delete certificate
  certificate:
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
        module.exit_json(changed=True, msg="certificate created")
    except Exception as e:
        module.fail_json(msg="Failed to create certificate: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="certificate updated")
    except Exception as e:
        module.fail_json(msg="Failed to update certificate: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="certificate deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete certificate: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read certificate: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'certificate_data': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'description': {'type': 'str'},
        'expiration_event_in': {'type': 'list', 'elements': 'str'},
        'format': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'key': {'type': 'str'},
        'key_data': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
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
            module.exit_json(changed=False, msg="certificate already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
