#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: folder
short_description: Manages a folder in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage folder resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    accessibility:
      description: "Folder accessibility: regular or personal"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the folder"
      type: str
    name:
      description: "Folder name"
      type: str
      required: true
    tags:
      description: "Tags for the folder"
      type: list
      elements: str
    type:
      description: ""
      type: str
'''

EXAMPLES = r'''
- name: Create folder
  folder:
    state: present

- name: Delete folder
  folder:
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
    'accessibility': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'tags': {'type': 'list', 'elements': 'str'},
    'type': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="folder",
        sdk_create=("FolderCreate", "folder_create"),
        sdk_update=("FolderUpdate", "folder_update"),
        sdk_delete=("FolderDelete", "folder_delete"),
        sdk_read=("FolderGet", "folder_get"),
    )


if __name__ == '__main__':
    main()
