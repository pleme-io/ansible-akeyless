# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    # Shared documentation for the authentication / transport parameters
    # that every module in this collection inherits via
    #   extends_documentation_fragment: drzln0.akeyless.auth
    #
    # The auth fields live on every module's argspec as a uniform shim
    # so callers can either pass them inline or rely on the AKEYLESS_*
    # environment variables. Documenting them once here keeps every
    # module's per-option doc terse and prevents the ~1000 sanity
    # errors that would otherwise fire from "undocumented-parameter"
    # / "parameter-type-not-in-doc" on every module.
    DOCUMENTATION = r'''
options:
    gateway_url:
        description:
            - URL of the Akeyless V2 API gateway.
            - Falls back to the C(AKEYLESS_GATEWAY_URL) environment variable, then
              to C(https://api.akeyless.io) if neither is set.
            - When using a self-hosted gateway, point this at the gateway's
              REST port (typically C(http://gateway.example.invalid:8081)).
            - The same URL works for both authentication and resource calls.
        type: str
    access_id:
        description:
            - Akeyless access ID (e.g. C(p-xxxxxxx)) used to authenticate.
            - Falls back to the C(AKEYLESS_ACCESS_ID) environment variable.
            - Recommended pattern in CI: set the env var once at the runner level
              so individual tasks stay free of credential references.
        type: str
    access_key:
        description:
            - Akeyless access key paired with I(access_id) for authentication.
            - Falls back to the C(AKEYLESS_ACCESS_KEY) environment variable.
            - Use C(no_log: true) on any task that references this inline.
        type: str
    access_type:
        description:
            - Akeyless authentication method.
            - Currently the modules only exercise C(access_key); other types are
              valid but not yet covered by per-module tests.
        type: str
        default: access_key
'''
