# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/lookup/secret.py -- the static-secret lookup
# plugin. Previously had zero test coverage; this file pins the
# loadability + auth-error + dispatch + reorder semantics.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
LOOKUP_PATH = REPO_ROOT / "plugins" / "lookup" / "secret.py"


def _install_ansible_lookup_stubs():
    """Stub ansible.plugins.lookup.LookupBase + ansible.errors.* so the
    secret lookup imports without a real Ansible install. We replace
    LookupBase with a minimal class that captures set_options() args
    and exposes get_option() against an internal dict.

    Also installs the shared lookup_auth helper at its
    ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth
    import path so the lookup's `from ansible_collections.<...>
    import authenticated_client` resolves under test."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleError"):
        class _StubAnsibleError(Exception):
            pass
        errors_mod.AnsibleError = _StubAnsibleError
    if not hasattr(errors_mod, "AnsibleLookupError"):
        class _StubAnsibleLookupError(Exception):
            pass
        errors_mod.AnsibleLookupError = _StubAnsibleLookupError

    if "ansible.plugins.lookup" not in sys.modules:
        plugins_mod = types.ModuleType("ansible.plugins")
        lookup_mod = types.ModuleType("ansible.plugins.lookup")

        class _StubLookupBase:
            def __init__(self):
                self._opts: dict = {}

            def set_options(self, var_options=None, direct=None):
                self._opts = dict(direct or {})
                for k, v in (var_options or {}).items():
                    self._opts.setdefault(k, v)

            def get_option(self, name):
                return self._opts.get(name)

        lookup_mod.LookupBase = _StubLookupBase
        sys.modules["ansible.plugins"] = plugins_mod
        sys.modules["ansible.plugins.lookup"] = lookup_mod
        ansible_pkg.plugins = plugins_mod

    # Register the lookup_auth helper at its ansible_collections.<...>
    # import path so the production lookups' `from ansible_collections
    # ...akeyless_lookup_auth import authenticated_client` resolves
    # under test. Re-uses _install_collection_helper_path's parent-
    # package setup pattern.
    parents = [
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ]
    for name in parents:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    helper_path = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"
    full = ("ansible_collections.drzln0.akeyless.plugins.module_utils"
            ".akeyless_lookup_auth")
    # Force fresh load so the helper's `import akeyless` rebinds to
    # whatever fake_akeyless installed for THIS test (otherwise the
    # first test wins and subsequent tests see a stale akeyless ref).
    sys.modules.pop(full, None)
    spec = importlib.util.spec_from_file_location(full, helper_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)


def _load_lookup(fake_akeyless):
    """Load the lookup module after stubbing ansible.errors/plugins."""
    _install_ansible_lookup_stubs()
    spec = importlib.util.spec_from_file_location(
        "akeyless_secret_lookup", LOOKUP_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_secret_lookup"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lookup(fake_akeyless):
    """Load the lookup with fake akeyless + ansible stubs in place."""
    fake_akeyless_mod, _ = fake_akeyless
    fake_akeyless_mod.GetSecretValue = MagicMock(name="akeyless.GetSecretValue")
    return _load_lookup(fake_akeyless_mod)


def test_lookup_module_class_exists(lookup):
    """LookupModule must be defined at module scope and subclass
    LookupBase (the stub or the real ansible.plugins.lookup.LookupBase)."""
    assert hasattr(lookup, "LookupModule")
    LookupModule = lookup.LookupModule
    from ansible.plugins.lookup import LookupBase
    assert issubclass(LookupModule, LookupBase)


def test_default_constants_match_collection_defaults(lookup):
    """The lookup must use the same gateway URL + access_type defaults
    as the helper module so behaviour is consistent across lookup vs
    module-task usage."""
    assert lookup.DEFAULT_GATEWAY_URL == "https://api.akeyless.io"
    assert lookup.DEFAULT_ACCESS_TYPE == "access_key"


def test_authenticated_client_uses_pre_issued_token(lookup):
    """When opts['token'] is set, _authenticated_client skips the auth
    call and returns the V2Api client + the verbatim token. Avoids the
    auth round-trip when the caller already has a session token (e.g.
    from a prior task)."""
    instance = lookup._authenticated_client({"token": "pre-issued-tok"})
    client, token = instance
    assert token == "pre-issued-tok"
    # The auth() method on the V2Api stub must NOT have been called.
    assert not client.auth.called


def test_authenticated_client_requires_access_id_when_no_token(lookup):
    """No token + no access_id -> AnsibleError. Catches misconfiguration
    that would otherwise surface as a 401 from the gateway."""
    from ansible.errors import AnsibleError
    with pytest.raises(AnsibleError, match="access_id is required"):
        lookup._authenticated_client({"token": None, "access_id": None})


def test_authenticated_client_runs_auth_path_when_no_token(lookup):
    """With access_id supplied, _authenticated_client calls client.auth
    with the constructed Auth body and returns its .token."""
    # Wire the akeyless stub's V2Api(...) -> client.auth -> AuthResponse
    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="resolved-token")
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)
    _, token = lookup._authenticated_client({
        "access_id": "p-xxx",
        "access_key": "secret==",
    })
    assert token == "resolved-token"
    fake_client.auth.assert_called_once()


def test_run_reorders_results_to_match_input_terms(lookup):
    """The Akeyless API returns a {name: value} dict; the lookup must
    reorder the response so the returned list matches the input term
    order. Critical for chained tasks that index by position."""
    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="tok")
    response = MagicMock()
    response.to_dict.return_value = {
        "/app/b": "value-of-b",
        "/app/a": "value-of-a",
        "/app/c": "value-of-c",
    }
    fake_client.get_secret_value.return_value = response
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)

    inst = lookup.LookupModule()
    out = inst.run(
        ["/app/a", "/app/b", "/app/c"],
        variables={},
        access_id="p-xxx", access_key="secret==",
    )
    assert out == ["value-of-a", "value-of-b", "value-of-c"]


def test_run_raises_lookup_error_when_secret_missing_from_response(lookup):
    """If the API doesn't return one of the requested secret names,
    surface an AnsibleLookupError naming the missing secret rather than
    silently dropping it (which would shift downstream indices)."""
    from ansible.errors import AnsibleLookupError

    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="tok")
    response = MagicMock()
    response.to_dict.return_value = {"/app/a": "v"}
    fake_client.get_secret_value.return_value = response
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)

    inst = lookup.LookupModule()
    with pytest.raises(AnsibleLookupError, match="not found"):
        inst.run(
            ["/app/a", "/app/missing"],
            variables={},
            access_id="p-xxx", access_key="secret==",
        )


def test_run_api_exception_raises_lookup_error(lookup):
    """A get_secret_value ApiException must surface as an
    AnsibleLookupError with the API's error body included -- helps
    users diagnose missing permissions / wrong path / etc."""
    from akeyless.exceptions import ApiException
    from ansible.errors import AnsibleLookupError

    fake_client = MagicMock(name="V2Api()")
    fake_client.auth.return_value = MagicMock(token="tok")
    fake_client.get_secret_value.side_effect = ApiException(
        status=403, body="forbidden"
    )
    lookup.akeyless.V2Api = MagicMock(return_value=fake_client)

    inst = lookup.LookupModule()
    with pytest.raises(AnsibleLookupError, match="403"):
        inst.run(["/app/a"], variables={}, access_id="p-xxx", access_key="x")
