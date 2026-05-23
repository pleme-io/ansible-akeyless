#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tokenizer
short_description: Manages a tokenizer in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
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

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

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
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='tokenizer',
        sdk_create=('CreateTokenizer', 'create_tokenizer'),
        sdk_update=None,
        sdk_delete=('DeleteItem', 'delete_item'),
        sdk_read=('DescribeItem', 'describe_item'),
        immutable=True,
    )


if __name__ == '__main__':
    main()
