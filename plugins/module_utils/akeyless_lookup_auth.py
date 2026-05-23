# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared auth helper for lookup + inventory plugins.

Lookup and inventory plugins each previously carried a ~50-line
`_authenticated_client(opts)` function. The duplication was historical
(believed to be a plugin-discovery sys.path limitation); confirmed
DRY-able at run time because ansible_collections module_utils ARE
on sys.path inside an actively-running play.

Centralising here means a single audited auth code path for every
non-module entry point (secret / dynamic_secret / pki_certificate
lookups + akeyless inventory). Pairs symmetrically with
plugins/module_utils/akeyless_client.py which handles auth for
modules via the same SDK primitives.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from typing import Any, Dict, Optional, Tuple

from ansible.errors import AnsibleError

try:
    import akeyless
    from akeyless.exceptions import ApiException
    HAS_AKEYLESS = True
    AKEYLESS_IMPORT_ERROR: Optional[ImportError] = None
except ImportError as exc:
    HAS_AKEYLESS = False
    AKEYLESS_IMPORT_ERROR = exc

DEFAULT_GATEWAY_URL = "https://api.akeyless.io"
DEFAULT_ACCESS_TYPE = "access_key"


def authenticated_client(opts: Dict[str, Any]) -> Tuple[Any, str]:
    """Resolve a V2Api client + access token from a flat opts dict.

    Precedence per field: opts[k] > AKEYLESS_<K> env > DEFAULT.
    `opts['token']` short-circuits the auth call when set.

    Raises AnsibleError (not AkeylessError) so the result surfaces
    cleanly through Ansible's playbook error machinery -- callers
    don't have to translate. Chains the underlying SDK ApiException
    via `raise X from exc` so `-vvv` traces show the original failure.
    """
    if not HAS_AKEYLESS:
        raise AnsibleError(
            "The 'akeyless' Python package is required. "
            "Install with: pip install 'akeyless>=5.0.22'. "
            f"Original error: {AKEYLESS_IMPORT_ERROR}"
        )

    gateway_url = opts.get("gateway_url") or DEFAULT_GATEWAY_URL
    config = akeyless.Configuration(host=gateway_url)
    client = akeyless.V2Api(akeyless.ApiClient(config))

    pre_issued = opts.get("token")
    if pre_issued:
        return client, pre_issued

    access_id = opts.get("access_id")
    if not access_id:
        raise AnsibleError(
            "access_id is required when no pre-issued token is provided "
            "(set the access_id option, AKEYLESS_ACCESS_ID env var, or pass token=...)"
        )

    auth_body = akeyless.Auth(
        access_id=access_id,
        access_key=opts.get("access_key"),
        access_type=opts.get("access_type") or DEFAULT_ACCESS_TYPE,
    )
    try:
        auth_res = client.auth(auth_body)
    except ApiException as exc:
        status = getattr(exc, "status", "?")
        raise AnsibleError(
            f"Akeyless auth failed ({status}): {exc.body or exc.reason}"
        ) from exc

    token = getattr(auth_res, "token", None)
    if not token:
        raise AnsibleError("Akeyless auth succeeded but returned no token")
    return client, token
