# Copyright: (c) 2026, pleme-io
# MIT License
#
# Session-scoped pytest fixtures that create real Akeyless resources
# (keys, roles, auth methods, groups, event forwarders) for the
# per-module coverage matrix to lean on. Without these, modules that
# need a pre-existing item end up in NEEDS_PREREQ category because
# the auto-stub path "/test-live/<run>/<module>" doesn't resolve to
# anything in the dev account.
#
# Lifecycle:
#   - All fixtures are scope="session" and use the same run_id so
#     concurrent xdist workers share them (one create per session,
#     not per worker).
#   - Names embed a per-session UUID under /test-live/fixtures/ so a
#     crashed run leaves a uniquely-named artifact that's safe to
#     ignore and easy to clean up by hand.
#   - Teardown is best-effort (try/except + finally) -- a failed
#     delete must never mask the underlying test failure.
#   - Each fixture validates its create succeeded by yielding the path
#     only after a non-exception return. If create raises ApiException,
#     pytest skips dependent tests with a clear reason.
#
# Add a new fixture pattern:
#   1) decorate with @pytest.fixture(scope="session")
#   2) call `_create_or_skip(...)` for the SDK create operation
#   3) yield the resource path/name
#   4) call `_safe_delete(...)` for cleanup
#
# Then wire it into _PREREQ_FIELD_MAP in coverage_matrix.py so the
# matching module(s) get the fixture's path injected as their
# identity field.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import uuid

import pytest


def pytest_addoption(parser):
    """Allow `--no-fixtures` to skip the whole fixture-creation phase
    when iterating on the matrix shape itself (faster, but the
    NEEDS_PREREQ modules will fail as before)."""
    parser.addoption(
        "--no-fixtures",
        action="store_true",
        default=False,
        help="Skip session-scoped Akeyless fixture creation. "
             "NEEDS_PREREQ modules will fall back to stubbed paths.",
    )


@pytest.fixture(scope="session")
def fixtures_enabled(request):
    return not request.config.getoption("--no-fixtures")


@pytest.fixture(scope="session")
def fixture_run_id():
    """A per-session UUID stamped into every fixture path. Decoupled
    from the matrix run_id (which is timestamp-based and used for
    test artifact paths) so fixtures aren't time-correlated."""
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="session")
def akeyless_client(fixtures_enabled):
    """A real V2Api client + token for the dev account. Skips the
    whole live-fixture set if the AKEYLESS_* env isn't present
    (CI without creds, or `--no-fixtures`)."""
    if not fixtures_enabled:
        pytest.skip("--no-fixtures requested")
    access_id = os.environ.get("AKEYLESS_ACCESS_ID")
    access_key = os.environ.get("AKEYLESS_ACCESS_KEY")
    gateway = os.environ.get("AKEYLESS_GATEWAY_URL", "https://api.akeyless.io")
    if not access_id or not access_key:
        pytest.skip("AKEYLESS_ACCESS_ID/KEY not set")

    import akeyless
    from akeyless.exceptions import ApiException
    cfg = akeyless.Configuration(host=gateway)
    client = akeyless.V2Api(akeyless.ApiClient(cfg))
    try:
        res = client.auth(akeyless.Auth(
            access_id=access_id, access_key=access_key, access_type="access_key"
        ))
    except ApiException as e:
        pytest.skip(f"akeyless auth failed: {e.body or e.reason}")
    token = getattr(res, "token", None)
    if not token:
        pytest.skip("akeyless auth returned no token")
    return client, token


# ---------------------------------------------------------------------- helpers


def _create_or_skip(client, sdk_model_name, body_attrs, method_name, label):
    """Build the SDK body, call the create method, return result or skip
    the dependent test with a clear reason.

    Tolerates "already exists" (returned when a prior run leaked the
    fixture) by treating it as success -- the resource is still there
    and usable by tests."""
    import akeyless
    from akeyless.exceptions import ApiException
    model = getattr(akeyless, sdk_model_name)
    method = getattr(client, method_name)
    try:
        return method(model(**body_attrs))
    except ApiException as e:
        msg = str(e.body or e.reason or "")
        if "already exists" in msg or "Already exists" in msg:
            return None
        pytest.skip(f"fixture {label} create failed: {msg[:200]}")


def _safe_delete(client, sdk_model_name, body_attrs, method_name, label):
    """Best-effort teardown. Logs a warning to stderr on failure but
    never raises -- a failed delete leaves an orphan but mustn't
    mask the test result."""
    import sys
    import akeyless
    from akeyless.exceptions import ApiException
    model = getattr(akeyless, sdk_model_name)
    method = getattr(client, method_name)
    try:
        method(model(**body_attrs))
    except ApiException as e:
        msg = str(e.body or e.reason or "")
        if "not found" in msg.lower() or "Status 404" in msg:
            return
        sys.stderr.write(f"[fixtures] WARN: cleanup of {label} failed: {msg[:200]}\n")
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[fixtures] WARN: cleanup of {label} crashed: {e}\n")


# ---------------------------------------------------------------------- fixtures


@pytest.fixture(scope="session")
def rsa_dfc_key(akeyless_client, fixture_run_id):
    """RSA2048 DFC key. Used by sign_pkcs1, generate_csr, ssh_cert_issuer
    (as the signer key), and pki_cert_issuer."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/rsa-dfc-key"
    _create_or_skip(client, "CreateDFCKey",
                    {"name": path, "alg": "RSA2048", "token": token},
                    "create_dfc_key", path)
    yield path
    _safe_delete(client, "DeleteItem",
                 {"name": path, "token": token, "delete_immediately": True},
                 "delete_item", path)


@pytest.fixture(scope="session")
def ec_classic_key(akeyless_client, fixture_run_id):
    """EC256 classic key for sign_ecdsa / verify_ecdsa. DFC keys don't
    support EC algorithms (only AES/RSA/SIV), so EC has to live as a
    classic key. The Akeyless SDK calls them by /name regardless of
    type, so callers just use the path."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/ec-classic-key"
    _create_or_skip(client, "CreateClassicKey",
                    {"name": path, "alg": "EC256", "token": token},
                    "create_classic_key", path)
    yield path
    _safe_delete(client, "DeleteItem",
                 {"name": path, "token": token, "delete_immediately": True},
                 "delete_item", path)


@pytest.fixture(scope="session")
def classic_key(akeyless_client, fixture_run_id):
    """RSA2048 classic key for sign_data_with_classic_key."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/classic-key"
    _create_or_skip(client, "CreateClassicKey",
                    {"name": path, "alg": "RSA2048", "token": token},
                    "create_classic_key", path)
    yield path
    _safe_delete(client, "DeleteItem",
                 {"name": path, "token": token, "delete_immediately": True},
                 "delete_item", path)


@pytest.fixture(scope="session")
def role(akeyless_client, fixture_run_id):
    """Bare role for role_auth_method_assoc / role_rule."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/role"
    _create_or_skip(client, "CreateRole",
                    {"name": path, "token": token},
                    "create_role", path)
    yield path
    _safe_delete(client, "DeleteRole",
                 {"name": path, "token": token},
                 "delete_role", path)


@pytest.fixture(scope="session")
def api_key_auth_method(akeyless_client, fixture_run_id):
    """API-key auth method for role_auth_method_assoc and auth_method_info.
    Akeyless requires audit_logs_claims to be a list."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/api-key-auth-method"
    _create_or_skip(client, "AuthMethodCreateApiKey",
                    {"name": path, "token": token},
                    "auth_method_create_api_key", path)
    yield path
    _safe_delete(client, "DeleteAuthMethod",
                 {"name": path, "token": token},
                 "delete_auth_method", path)


@pytest.fixture(scope="session")
def uid_auth_method(akeyless_client, fixture_run_id):
    """Universal-Identity auth method for uid_generate_token."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/uid-auth-method"
    _create_or_skip(client, "AuthMethodCreateUniversalIdentity",
                    {"name": path, "ttl": 60, "token": token},
                    "auth_method_create_universal_identity", path)
    yield path
    _safe_delete(client, "DeleteAuthMethod",
                 {"name": path, "token": token},
                 "delete_auth_method", path)


@pytest.fixture(scope="session")
def group(akeyless_client, fixture_run_id):
    """Group for group_info. CreateGroup requires `group_alias` and a
    parseable `user_assignment` (an empty JSON array is fine for a
    bare fixture group)."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/group"
    alias = f"fx-{fixture_run_id}"
    _create_or_skip(client, "CreateGroup",
                    {
                        "name": path,
                        "group_alias": alias,
                        "user_assignment": "[]",
                        "token": token,
                    },
                    "create_group", path)
    yield path
    _safe_delete(client, "DeleteGroup",
                 {"name": path, "token": token},
                 "delete_group", path)


@pytest.fixture(scope="session")
def email_event_forwarder(akeyless_client, fixture_run_id):
    """Email event forwarder for event_forwarder_info. Akeyless's create
    requires runner_type + gateways_event_source_locations + email_to."""
    client, token = akeyless_client
    path = f"/test-live/fixtures/{fixture_run_id}/email-event-forwarder"
    _create_or_skip(client, "EventForwarderCreateEmail",
                    {
                        "name": path,
                        "runner_type": "immediate",
                        "email_to": "fixtures@example.invalid",
                        "gateways_event_source_locations": ["*"],
                        "event_types": ["request-access"],
                        "token": token,
                    },
                    "event_forwarder_create_email", path)
    yield path
    _safe_delete(client, "EventForwarderDelete",
                 {"name": path, "token": token},
                 "event_forwarder_delete", path)
