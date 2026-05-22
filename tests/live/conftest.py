# Copyright: (c) 2026, pleme-io
# MIT License
#
# Re-export session-scoped Akeyless fixtures so pytest auto-discovers
# them for every test under tests/live/. Keep fixture definitions in
# fixtures.py (importable as a normal module) so callers outside the
# tests dir can also use them.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .fixtures import (  # noqa: F401
    pytest_addoption,
    fixtures_enabled,
    fixture_run_id,
    akeyless_client,
    rsa_dfc_key,
    ec_classic_key,
    classic_key,
    role,
    api_key_auth_method,
    uid_auth_method,
    group,
    email_event_forwarder,
)
