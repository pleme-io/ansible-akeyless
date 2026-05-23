# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: parse_dotenv_secret
short_description: Parse a dotenv-formatted secret into a dict
version_added: "0.2.5"
description:
  - "Parses an Akeyless secret value containing dotenv-style
    C(KEY=value) lines into a C({key: value}) dict."
  - "Accepts C(export KEY=value) (prefix stripped), single/double
    quoted values (quotes stripped), and skips blank lines + comments
    (C(#)-prefixed)."
  - "Raises C(AnsibleFilterError) on lines missing the C(=) separator."
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Dotenv-formatted secret value.
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Run app with secrets-from-vault env
  ansible.builtin.command: ./app
  environment: "{{ lookup('drzln0.akeyless.secret', '/app/.env')
                   | drzln0.akeyless.parse_dotenv_secret }}"
'''

RETURN = r'''
_value:
  description: A dict of {key, value} parsed from the dotenv-formatted input.
  type: dict
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    parse_dotenv_secret,
)


class FilterModule:
    def filters(self):
        return {"parse_dotenv_secret": parse_dotenv_secret}
