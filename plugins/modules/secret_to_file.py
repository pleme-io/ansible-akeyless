#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: secret_to_file
short_description: Fetch an Akeyless static secret and write it to a remote file
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Atomic from the playbook's POV - one task = one secret materialized
    on the target.
  - Implemented as an action plugin (plugins/action/secret_to_file.py)
    that fetches the secret on the controller and writes it via
    ansible.builtin.copy. The secret value never appears in task-arg
    rendering or verbose logging.
options:
    secret:
      description: "Akeyless secret path (e.g. /app/db/password)."
      type: str
      required: true
    dest:
      description: "Path to write the secret on the target host."
      type: path
      required: true
    owner:
      description: "Owner for the destination file. Defaults to ansible_user."
      type: str
    group:
      description: "Group for the destination file."
      type: str
    mode:
      description: 'File mode (e.g. "0600", "u=rw,g=,o="). Defaults to a restrictive 0600.'
      type: str
    backup:
      description: "Create a timestamped backup of the existing file when content changes."
      type: bool
      default: false
    force:
      description: "Overwrite the destination even when content hasn't changed."
      type: bool
      default: true
'''

EXAMPLES = r'''
- name: Install DB password from Akeyless onto the target
  drzln0.akeyless.secret_to_file:
    secret: /app/prod/db/password
    dest: /etc/app/db.pass
    owner: app
    group: app
    mode: '0600'
    backup: true
'''

RETURN = r'''
# Inherits ansible.builtin.copy's return shape (changed, dest, size, etc.).
'''


def main():
    # Action plugins shadow module wrappers of the same name. This
    # stub exists only so ansible-doc + collection sanity find the
    # DOCUMENTATION block; the real work happens in
    # plugins/action/secret_to_file.py at controller-side run time.
    from ansible.module_utils.basic import AnsibleModule
    AnsibleModule(
        argument_spec={
            'secret': {'type': 'str', 'required': True},
            'dest': {'type': 'path', 'required': True},
            'owner': {'type': 'str'},
            'group': {'type': 'str'},
            'mode': {'type': 'str'},
            'backup': {'type': 'bool', 'default': False},
            'force': {'type': 'bool', 'default': True},
            'gateway_url': {'type': 'str'},
            'access_id': {'type': 'str'},
            'access_key': {'type': 'str', 'no_log': True},
            'access_type': {'type': 'str', 'default': 'access_key'},
        },
        supports_check_mode=True,
    ).exit_json(changed=False, msg=(
        "secret_to_file is an action plugin and shouldn't be invoked "
        "directly as a module. Ensure the action plugin path is on "
        "ANSIBLE_ACTION_PLUGINS or that the collection is installed "
        "via `ansible-galaxy collection install drzln0.akeyless`."
    ))


if __name__ == '__main__':
    main()
