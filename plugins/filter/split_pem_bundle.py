# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: split_pem_bundle
short_description: Split a multi-cert PEM bundle into individual blocks
version_added: "0.2.5"
description:
  - Splits a multi-cert PEM bundle into a list of individual PEM
    blocks. Useful for processing CA bundles where each cert must
    be installed to a separate file (e.g. systemd-style
    C(/etc/ssl/certs/<hash>.0) layout).
  - Each block includes its C(-----BEGIN/END-----) markers verbatim.
  - Skips blank lines + content outside of begin/end markers. Raises
    C(AnsibleFilterError) on orphan C(-----END) markers or
    unterminated C(-----BEGIN) blocks.
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: PEM bundle text.
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Install each trust root separately
  ansible.builtin.copy:
    content: "{{ item }}"
    dest: "/etc/ssl/certs/akeyless-{{ index }}.pem"
  loop: "{{ lookup('drzln0.akeyless.secret', '/ca/bundle')
            | drzln0.akeyless.split_pem_bundle }}"
  loop_control:
    index_var: index
'''

RETURN = r'''
_value:
  description: List of individual PEM blocks (each includes its BEGIN/END markers).
  type: list
  elements: str
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    split_pem_bundle,
)


class FilterModule:
    def filters(self):
        return {"split_pem_bundle": split_pem_bundle}
