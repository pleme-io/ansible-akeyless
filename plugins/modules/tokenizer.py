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
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("CreateTokenizer", dict(module.params, token=token))
    return call_api(module, client, "create_tokenizer", body)


def update_resource(module, client, token):
    """Update not supported by the upstream API -- delete + recreate instead."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    module.fail_json(msg="tokenizer: update not supported, delete+recreate")


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
        module.exit_json(changed=False, msg="tokenizer already absent")
    else:
        if current is None:
            result = create_resource(module, client, token)
            module.exit_json(changed=True, result=result)
        result = update_resource(module, client, token)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
