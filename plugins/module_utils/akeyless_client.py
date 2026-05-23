# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# MIT License
#
# Auto-generated module utility for the Akeyless V2 API.
# This file ships at plugins/module_utils/akeyless_client.py.
# All generated resource modules import get_client, call_api, build_body
# from here -- it is the only place that touches the akeyless SDK directly.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import inspect
import os

try:
    import akeyless
    from akeyless.exceptions import ApiException
    HAS_AKEYLESS = True
    AKEYLESS_IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - exercised by Ansible at runtime
    HAS_AKEYLESS = False
    AKEYLESS_IMPORT_ERROR = exc

DEFAULT_GATEWAY_URL = "https://api.akeyless.io"
DEFAULT_ACCESS_TYPE = "access_key"


def _require_sdk(module):
    if not HAS_AKEYLESS:
        module.fail_json(
            msg="The 'akeyless' Python package is required. Install with 'pip install akeyless>=5.0.22'.",
            exception=str(AKEYLESS_IMPORT_ERROR),
        )


def get_client(module):
    """Return (V2Api client, access token) for the module's auth params.

    Resolves gateway/credentials from (in priority order):
      1. module.params['gateway_url' | 'access_id' | 'access_key' | 'access_type']
      2. AKEYLESS_GATEWAY_URL / AKEYLESS_ACCESS_ID / AKEYLESS_ACCESS_KEY env vars
      3. AKEYLESS_TOKEN env var (used directly as token; no auth call performed)
    """
    _require_sdk(module)

    params = module.params or {}
    gateway_url = params.get("gateway_url") or os.environ.get("AKEYLESS_GATEWAY_URL") or DEFAULT_GATEWAY_URL
    access_id = params.get("access_id") or os.environ.get("AKEYLESS_ACCESS_ID")
    access_key = params.get("access_key") or os.environ.get("AKEYLESS_ACCESS_KEY")
    access_type = params.get("access_type") or DEFAULT_ACCESS_TYPE

    configuration = akeyless.Configuration(host=gateway_url)
    client = akeyless.V2Api(akeyless.ApiClient(configuration))

    pre_issued = os.environ.get("AKEYLESS_TOKEN")
    if pre_issued:
        return client, pre_issued

    if not access_id:
        module.fail_json(msg="access_id is required (set module param or AKEYLESS_ACCESS_ID env)")

    auth_body = akeyless.Auth(access_id=access_id, access_key=access_key, access_type=access_type)
    try:
        auth_res = client.auth(auth_body)
    except ApiException as exc:
        module.fail_json(msg="Akeyless auth failed: %s" % (exc.body or exc.reason), status=getattr(exc, "status", None))
    token = getattr(auth_res, "token", None)
    if not token:
        module.fail_json(msg="Akeyless auth returned no token")
    return client, token


def build_body(model_class_name, params):
    """Instantiate akeyless.<model_class_name>(**filtered_params).

    Filters params to those the model accepts AND drops None values.
    """
    _ensure_sdk_loaded()
    model_cls = getattr(akeyless, model_class_name, None)
    if model_cls is None:
        raise ValueError("Unknown Akeyless model: %s" % model_class_name)
    try:
        accepted = set(inspect.signature(model_cls.__init__).parameters)
    except (TypeError, ValueError):
        accepted = set(getattr(model_cls, "attribute_map", {}).keys())
    filtered = {k: v for k, v in (params or {}).items() if v is not None and k in accepted}
    return model_cls(**filtered)


def call_api(module, client, method_name, body, swallow_404=False):
    """Invoke client.<method_name>(body) and return a dict.

    If swallow_404 is true, a 404 ApiException returns None instead of
    failing the module -- used by read_resource to detect absence.

    Per-call timeout is read from AKEYLESS_REQUEST_TIMEOUT env (seconds,
    float). Unset/0 means no SDK-level timeout (akeyless default).
    Useful for `live-coverage-gateway` runs where a local gateway tries
    to validate stub data against the real internet and hangs.
    """
    method = getattr(client, method_name, None)
    if method is None:
        module.fail_json(msg="Akeyless V2Api has no method '%s'" % method_name)
    try:
        result = _invoke_sdk_method(method, method_name, body)
    except ApiException as exc:
        status = getattr(exc, "status", None)
        if swallow_404 and status == 404:
            return None
        module.fail_json(
            msg="Akeyless API call %s failed: %s" % (method_name, exc.body or exc.reason),
            status=status,
        )
    return _to_dict(result)


def _invoke_sdk_method(method, method_name, body):
    """Call an akeyless V2Api method with a body, tolerating both
    positional-body and kwargs-only SDK shapes.

    Most generated SDK methods take the body positionally
    (`method(body)`). A handful are declared as `def m(self, **kwargs)`
    and expect the body keyword-named after the snake_case method name
    (`method(<method_name>=body)`). We try positional first and fall
    back to the kwarg form on the exact TypeError that signals the
    second shape, so callers don't need to know which SDK style applies."""
    timeout_env = os.environ.get("AKEYLESS_REQUEST_TIMEOUT")
    kwargs = {}
    if timeout_env:
        try:
            kwargs["_request_timeout"] = float(timeout_env)
        except ValueError:
            pass
    try:
        return method(body, **kwargs) if kwargs else method(body)
    except TypeError as exc:
        if "takes 1 positional argument but 2 were given" in str(exc):
            return method(**{method_name: body}, **kwargs)
        raise


def _to_dict(result):
    if result is None:
        return None
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if isinstance(result, dict):
        return result
    return {"result": result}


def _ensure_sdk_loaded():
    if not HAS_AKEYLESS:
        raise RuntimeError("akeyless SDK not importable: %s" % AKEYLESS_IMPORT_ERROR)


# Keys present on every module's argspec for auth/meta plumbing -- never
# part of the desired resource state and so always excluded from drift
# detection. Includes `state` (Ansible directive), `token`/`uid_token`
# (per-call auth), and the AKEYLESS_* shim params.
IDEMPOTENCY_IGNORE_KEYS = frozenset({
    "state",
    "token", "uid_token",
    "gateway_url", "access_id", "access_key", "access_type",
    # SDK pagination/format flags that shouldn't drive convergence
    "json",
})


# Common nested paths an Akeyless Get response uses to wrap the actual
# resource fields. Tried in order when a desired param isn't found at
# the top level of the read dict.
_NESTED_PATHS = (
    "target_details",
    "item_details",
    "auth_method_details",
    "secret_details",
    "rules",            # role_get
    "value",            # generic SDK envelope
)


def _snake_to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def _lookup(current, key):
    """Find `key` in a possibly-nested SDK Get response dict.

    Tries snake_case at the top level, then each common nested path,
    then a camelCase fallback. Returns None if nowhere."""
    if not isinstance(current, dict):
        return None
    if key in current:
        return current[key]
    camel = _snake_to_camel(key)
    if camel in current:
        return current[camel]
    for nest in _NESTED_PATHS:
        sub = current.get(nest)
        if isinstance(sub, dict):
            if key in sub:
                return sub[key]
            if camel in sub:
                return sub[camel]
    return None


def compute_diff(current, params, ignore=None):
    """Drift detection for idempotent update: return [(key, before, after)]
    for each `params` field whose non-None value disagrees with what's
    in the SDK Get response.

    Skips params with value None (the user hasn't asked to set them),
    keys in `ignore` (defaults to IDEMPOTENCY_IGNORE_KEYS), and any
    fields that don't appear in `current` at all (we can't honestly
    say they drifted if the SDK never echoes them back). This is
    conservative on purpose -- a false "in-sync" verdict surfaces as
    a no-op that the user can correct, while a false drift verdict
    would call update() unnecessarily and report changed=True every
    run, defeating the point.
    """
    if not isinstance(current, dict) or not params:
        return []
    ignore = ignore or IDEMPOTENCY_IGNORE_KEYS
    drift = []
    for key, desired in params.items():
        if desired is None or key in ignore:
            continue
        cur = _lookup(current, key)
        if cur is None:
            # Field absent from the read response -- skip rather than
            # treat as drift. The SDK may not echo write-only fields
            # (passwords, tokens, etc.) so missing != different.
            continue
        if cur != desired:
            drift.append((key, cur, desired))
    return drift


def drift_to_diff(drift):
    """Convert the (key, before, after) tuples from compute_diff into
    the {"before": {...}, "after": {...}} shape Ansible's diff mode
    expects in exit_json(diff=...)."""
    return {
        "before": {k: b for k, b, _ in drift},
        "after":  {k: a for k, _, a in drift},
    }


def run_standard_crud(
    argument_spec,
    resource_label,
    sdk_create,
    sdk_update,
    sdk_delete,
    sdk_read,
    read_key="name",
    required_if=None,
    immutable=False,
):
    """Drive the full create/read/update/delete lifecycle for a
    standard-shape Akeyless resource module. Replaces the ~80 lines of
    boilerplate that used to live in every plugins/modules/*.py.

    Per-module callers supply:

      argument_spec    AnsibleModule argument spec dict (incl. the
                       auth shim: gateway_url/access_id/access_key/
                       access_type, and the state choice).
      resource_label   Human-readable name used in the
                       "already absent"/"already in desired state"
                       messages (e.g. "auth_method_oidc").
      sdk_create       Tuple ("ModelClassName", "snake_method_name")
                       that build_body and call_api hand off to.
      sdk_update       Same shape; some resources reuse a generic
                       update model (e.g. "TargetUpdate" / variant).
      sdk_delete       Same shape; many resources route to a shared
                       delete endpoint ("delete_item" /
                       "delete_auth_method" / "target_delete").
      sdk_read         Same shape; the get/describe endpoint that
                       returns the resource's current state.
      read_key         Argspec field whose value identifies the
                       resource on the read call. Defaults to "name";
                       a tiny number of modules (e.g. target_windows)
                       use "hostname".
      required_if      Forwarded verbatim to AnsibleModule(); pass
                       e.g. [("state", "present", ["value"])] for
                       modules where a field is mandatory only on
                       create/update.
      immutable        When True, the resource has no upstream Update
                       endpoint -- drift triggers fail_json("delete+
                       recreate required") instead of an update call.
                       Pass `sdk_update=None` in that case; the helper
                       won't dereference it.

    Behavior:
      - Reads current state via sdk_read (404 → resource absent).
      - state=absent: deletes if present, else changed=False with
        "<resource_label> already absent".
      - state=present + absent: creates via sdk_create.
      - state=present + present + no drift: changed=False with
        "<resource_label> already in desired state".
      - state=present + present + drift: updates via sdk_update and
        emits Ansible-shape diff metadata ({before, after}).
      - check_mode is honored at every write point.
    """
    from ansible.module_utils.basic import AnsibleModule

    module_kwargs = {"argument_spec": argument_spec, "supports_check_mode": True}
    if required_if:
        module_kwargs["required_if"] = required_if
    module = AnsibleModule(**module_kwargs)

    client, token = get_client(module)
    state = module.params.get("state", "present")

    # Read current state. read_key isolates which *argspec field*
    # carries the resource identifier (most modules use "name", a few
    # like role_auth_method_assoc use "role_name"). The SDK Get model
    # itself always names the field `name`, so we pass the value through
    # under `name` regardless of read_key. build_body will then filter
    # to whatever the specific model's __init__ accepts.
    create_model, create_method = sdk_create
    delete_model, delete_method = sdk_delete
    read_model,   read_method   = sdk_read
    if immutable:
        update_model = update_method = None
    else:
        update_model, update_method = sdk_update

    read_body = build_body(read_model, {
        "name": module.params.get(read_key),
        read_key: module.params.get(read_key),  # tolerate models that use the same name as the argspec field
        "token": token,
    })
    current = call_api(module, client, read_method, read_body, swallow_404=True)

    if state == "absent":
        if current is None:
            module.exit_json(changed=False, msg=f"{resource_label} already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        body = build_body(delete_model, dict(module.params, token=token))
        result = call_api(module, client, delete_method, body)
        module.exit_json(changed=True, result=result)

    # state == "present"
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        body = build_body(create_model, dict(module.params, token=token))
        result = call_api(module, client, create_method, body)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs from
    # what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False,
                         msg=f"{resource_label} already in desired state")
    diff = drift_to_diff(drift)
    if immutable:
        # Resource exists, drift detected, but no upstream Update
        # endpoint. Surface the diff so the user can see what would
        # change, then fail with explicit guidance.
        module.fail_json(
            msg=(f"{resource_label}: drift detected but the resource is "
                 "immutable after creation; delete and re-create with the "
                 "new values"),
            diff=diff,
        )
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    body = build_body(update_model, dict(module.params, token=token))
    result = call_api(module, client, update_method, body)
    module.exit_json(changed=True, result=result, diff=diff)


def run_action_module(argument_spec, sdk_call, supports_check_mode=False):
    """Drive a one-shot non-CRUD module. Replaces the run_action +
    main() boilerplate that the ~26 action modules (uid_generate_token,
    sign_pkcs1, encrypt, decrypt, generate_ca, …) carried.

      argument_spec        AnsibleModule argument spec.
      sdk_call             Tuple ("ModelClassName", "snake_method_name").
      supports_check_mode  Whether AnsibleModule should advertise it.
                           Defaults to False because action modules
                           are imperative one-shots -- check_mode has
                           no meaningful "would-do" semantics for
                           "sign this message" or "rotate this token".

    Behavior: build_body → call_api → exit_json(changed=True,
    result=<sdk response dict>). The action label is whatever Ansible
    Galaxy displays via the module name; no extra labelling needed.
    """
    from ansible.module_utils.basic import AnsibleModule

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=supports_check_mode,
    )
    client, token = get_client(module)
    sdk_model, sdk_method = sdk_call
    body = build_body(sdk_model, dict(module.params, token=token))
    result = call_api(module, client, sdk_method, body)
    module.exit_json(changed=True, result=result)
