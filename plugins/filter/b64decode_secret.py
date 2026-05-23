# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: b64decode_secret
short_description: Strict-validating base64 decoder for secret payloads
version_added: "0.2.5"
description:
  - Base64-decodes a secret string returned by Akeyless (keys, certs,
    .pfx blobs, etc.) and returns the decoded text.
  - Uses C(validate=True) so non-base64 alphabet characters are
    rejected with C(AnsibleFilterError) rather than silently stripped
    (Python's default). For secret-handling, strict failure is the
    safe default.
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Base64-encoded secret string.
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Decode a base64-encoded cert secret
  ansible.builtin.set_fact:
    cert_pem: "{{ lookup('drzln0.akeyless.secret', '/certs/app')
                  | drzln0.akeyless.b64decode_secret }}"
'''

RETURN = r'''
_value:
  description: UTF-8 decoded payload.
  type: str
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    b64decode_secret,
)


class FilterModule:
    def filters(self):
        return {"b64decode_secret": b64decode_secret}
