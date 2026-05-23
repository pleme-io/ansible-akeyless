#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Action plugin: drzln0.akeyless.secret_to_file.

Fetches an Akeyless static secret on the controller and writes its
value to a remote file via the standard ansible.builtin.copy module.
Atomic from the user's POV (one task = one secret materialized on the
target) and never leaks the value through Ansible task-arg rendering.

The matching module wrapper is plugins/modules/secret_to_file.py --
this action plugin is what actually runs (action plugins shadow
module wrappers of the same name).
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from typing import Any, Dict

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Controller-side: fetch secret, hand to copy module on target."""

    TRANSFERS_FILES = True

    # Args this action accepts on the task. `secret` + `dest` are
    # required; the rest mirror ansible.builtin.copy's interface so
    # users can apply the usual perms / ownership / backup options
    # without learning a separate vocabulary.
    _VALID_ARGS = frozenset({
        "secret",   # Akeyless secret path
        "dest",     # target file path
        "owner", "group", "mode", "backup", "force",
        # Auth options (also resolved from env/playbook-level vars)
        "gateway_url", "access_id", "access_key", "access_type", "token",
    })

    def run(self, tmp: Any = None, task_vars: Any = None) -> Dict[str, Any]:
        task_vars = task_vars or {}
        result = super().run(tmp, task_vars)
        del tmp  # unused; required by ActionBase signature

        # Validate required args before any SDK round-trip.
        args = self._task.args or {}
        secret = args.get("secret")
        dest = args.get("dest")
        if not secret:
            raise AnsibleActionFail("'secret' is required (an Akeyless secret path)")
        if not dest:
            raise AnsibleActionFail("'dest' is required (a target file path)")
        unknown = set(args) - self._VALID_ARGS
        if unknown:
            raise AnsibleActionFail(
                f"Unknown args for drzln0.akeyless.secret_to_file: {sorted(unknown)}"
            )

        # Fetch the secret via the existing lookup plugin -- we already
        # have its auth handling, batching, and error model. Build the
        # lookup options from the action's args (so per-task overrides
        # work like they do everywhere else in the collection).
        try:
            secret_value = self._templar.template(
                "{{ lookup('drzln0.akeyless.secret', secret, **lookup_opts) }}",
                fail_on_undefined=True,
            )
        except Exception:
            # Fall back to the direct lookup invocation when templar
            # isn't usable (e.g. some unit-test contexts).
            from ansible.plugins.loader import lookup_loader
            lookup = lookup_loader.get(
                "drzln0.akeyless.secret",
                loader=self._loader,
                templar=self._templar,
            )
            lookup_opts = {
                k: args[k]
                for k in ("gateway_url", "access_id", "access_key",
                          "access_type", "token")
                if k in args
            }
            values = lookup.run([secret], variables=task_vars, **lookup_opts)
            secret_value = values[0] if values else None
        if secret_value is None:
            raise AnsibleActionFail(
                f"Akeyless returned no value for secret {secret!r}"
            )

        # Delegate to ansible.builtin.copy on the target. Pass the
        # secret value via `content` -- copy materializes it through
        # the action's transfer mechanism, so the value never appears
        # in task arg rendering / verbose logging.
        copy_args = {
            "content": secret_value,
            "dest": dest,
        }
        for opt in ("owner", "group", "mode", "backup", "force"):
            if opt in args:
                copy_args[opt] = args[opt]

        copy_result = self._execute_module(
            module_name="ansible.builtin.copy",
            module_args=copy_args,
            task_vars=task_vars,
        )

        # Merge the copy result into our result. Strip the secret
        # value from any echoed args defensively (copy redacts
        # `content` by default but be paranoid).
        result.update(copy_result)
        if isinstance(result.get("invocation"), dict):
            ma = result["invocation"].get("module_args")
            if isinstance(ma, dict) and "content" in ma:
                ma["content"] = "*** redacted by drzln0.akeyless.secret_to_file ***"
        return result
