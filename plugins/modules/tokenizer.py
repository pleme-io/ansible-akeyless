#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tokenizer
short_description: Manages a tokenizer in Akeyless Vault
description:
  - Manage tokenizer resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    alphabet:
      description: "Alphabet to use in regexp vaultless tokenization"
      type: str
    decoding_template:
      description: "The Decoding output template to use in regexp vaultless tokenization"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    description:
      description: "Description of the object"
      type: str
    encoding_template:
      description: "The Encoding output template to use in regexp vaultless tokenization"
      type: str
    encryption_key_name:
      description: "AES key name to use in vaultless tokenization"
      type: str
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Tokenizer name"
      type: str
      required: true
    pattern:
      description: "Pattern to use in regexp vaultless tokenization"
      type: str
    tag:
      description: "List of the tags attached to this key"
      type: list
      elements: str
    template_type:
      description: "Which template type this tokenizer is used for [SSN,CreditCard,USPhoneNumber,Email,Regexp]"
      type: str
      required: true
    tokenizer_type:
      description: "Tokenizer type"
      type: str
      required: true
    tweak_type:
      description: "The tweak type to use in vaultless tokenization [Supplied, Generated, Internal, Masking]"
      type: str
'''

EXAMPLES = r'''
- name: Create tokenizer
  tokenizer:
    state: present

- name: Delete tokenizer
  tokenizer:
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
        module.exit_json(changed=True, msg="tokenizer created")
    except Exception as e:
        module.fail_json(msg="Failed to create tokenizer: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="tokenizer updated")
    except Exception as e:
        module.fail_json(msg="Failed to update tokenizer: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="tokenizer deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete tokenizer: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read tokenizer: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'alphabet': {'type': 'str'},
        'decoding_template': {'type': 'str'},
        'delete_protection': {'type': 'str'},
        'description': {'type': 'str'},
        'encoding_template': {'type': 'str'},
        'encryption_key_name': {'type': 'str'},
        'item_custom_fields': {'type': 'dict'},
        'name': {'type': 'str', 'required': True},
        'pattern': {'type': 'str'},
        'tag': {'type': 'list', 'elements': 'str'},
        'template_type': {'type': 'str', 'required': True},
        'tokenizer_type': {'type': 'str', 'required': True},
        'tweak_type': {'type': 'str'},
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
            module.exit_json(changed=False, msg="tokenizer already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
