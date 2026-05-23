# Copyright: (c) 2026, pleme-io
# MIT License
#
# Shared mock-server infrastructure for lookup-plugin integration
# tests. Three lookup integration files (secret, dynamic_secret,
# pki_certificate) previously duplicated ~50 LOC each of stub
# installation + MockServer scaffolding. They now all import this
# module.
#
# Why a non-conftest module: each lookup test wants its own _LookupMockServer
# instance + needs to bind the right SDK method onto the V2Api proxy
# (get_secret_value vs get_dynamic_secret_value vs get_pki_certificate).
# A conftest fixture would force all three to share state; a plain
# importable factory keeps each test isolated.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from unittest.mock import MagicMock

from .conftest import FakeApiException

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOKUP_AUTH_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"
PLUGIN_HELPERS_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"


class LookupMockServer:
    """Tiny endpoint registry shared by every lookup integration test.

    Each `on(method_name, response=...)` declares what the proxy
    returns when the lookup invokes that SDK method. Each
    `_dispatch(method_name, body)` is what the proxy actually calls
    -- the caller wires the proxy's getattr/method definitions to
    route through here.
    """

    def __init__(self):
        self._handlers: Dict[str, tuple] = {}
        self.calls: list = []

    def on(
        self,
        method_name: str,
        response: Optional[Any] = None,
        raises: Optional[Exception] = None,
        callable_factory: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        """Register a handler for `method_name`.

        Exactly one of `response` / `raises` / `callable_factory`
        must be supplied:
        - response (dict)     -> wrap into a MagicMock with .to_dict()
        - response (other)    -> return verbatim
        - raises (Exception)  -> raise it
        - callable_factory(body) -> per-call result; the dispatcher
          wraps it into a MagicMock with .to_dict() (used by the
          dynamic-secret lookup test for per-term responses).
        """
        if raises is not None:
            self._handlers[method_name] = ("raise", raises)
        elif callable_factory is not None:
            self._handlers[method_name] = ("callable", callable_factory)
        elif isinstance(response, dict):
            self._handlers[method_name] = ("dict", response)
        else:
            self._handlers[method_name] = ("raw", response)

    def _dispatch(self, method_name: str, body: Any) -> Any:
        self.calls.append((method_name, body))
        if method_name not in self._handlers:
            raise FakeApiException(
                status=500,
                body=f"mock-server: no handler for {method_name!r}",
            )
        kind, payload = self._handlers[method_name]
        if kind == "raise":
            raise payload
        if kind == "callable":
            m = MagicMock(name=f"{method_name}_response")
            m.to_dict.return_value = payload(body)
            return m
        if kind == "dict":
            m = MagicMock(name=f"{method_name}_response")
            m.to_dict.return_value = payload
            return m
        return payload


def install_lookup_stubs(
    server: LookupMockServer,
    *,
    sdk_method_name: str,
    sdk_body_class_name: Optional[str] = None,
    body_capture: Optional[dict] = None,
    extra_akeyless_attrs: Optional[Dict[str, Any]] = None,
) -> None:
    """Install the standard set of ansible / akeyless / collection-
    helper stubs the lookup needs to import + run.

    Parameters:
      server: the LookupMockServer instance the V2Api proxy routes to.
      sdk_method_name: the name of the SDK method the lookup calls
        on the V2Api proxy (e.g. "get_secret_value",
        "get_dynamic_secret_value", "get_pki_certificate").
      sdk_body_class_name: optional. When set, replace the fake
        akeyless.<name>(...) class with a small recorder that stores
        its kwargs in `body_capture` so tests can assert on what the
        lookup passed.
      body_capture: mutable dict the body-class recorder writes into.
      extra_akeyless_attrs: optional extras to bolt onto the fake
        akeyless module (e.g. specific MagicMock for a body class).
    """
    # ansible.errors with AnsibleError + AnsibleLookupError.
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    for cls_name in ("AnsibleError", "AnsibleLookupError"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))

    # ansible.plugins.lookup.LookupBase with a stub that mirrors the
    # real option-resolution shape (`set_options(direct=...)`
    # then `get_option(name)`).
    plugins_pkg = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    lookup_mod = sys.modules.setdefault(
        "ansible.plugins.lookup", types.ModuleType("ansible.plugins.lookup")
    )
    plugins_pkg.lookup = lookup_mod
    ansible_pkg.plugins = plugins_pkg
    if not hasattr(lookup_mod, "LookupBase"):
        class _LookupBase:
            def __init__(self):
                self._opts: dict = {}

            def set_options(self, var_options=None, direct=None):
                self._opts = dict(direct or {})
                for k, v in (var_options or {}).items():
                    self._opts.setdefault(k, v)

            def get_option(self, name):
                return self._opts.get(name)

        lookup_mod.LookupBase = _LookupBase

    # akeyless SDK: V2Api(...) returns a proxy whose `auth()` is a
    # no-op (returns a token) and whose `<sdk_method_name>(body)`
    # routes through the supplied server.
    class _Proxy:
        def __init__(self, _server: LookupMockServer):
            self._server = _server

        def auth(self, _body):
            r = MagicMock()
            r.token = "mock-token"
            return r

        def __getattr__(self, name):
            if name == sdk_method_name:
                return lambda body: self._server._dispatch(name, body)
            raise AttributeError(name)

    akeyless_mod = types.ModuleType("akeyless")
    akeyless_mod.Configuration = MagicMock(name="akeyless.Configuration")
    akeyless_mod.ApiClient = MagicMock(name="akeyless.ApiClient")
    akeyless_mod.V2Api = MagicMock(
        name="akeyless.V2Api", return_value=_Proxy(server)
    )
    akeyless_mod.Auth = MagicMock(name="akeyless.Auth")

    # Optional body-class recorder.
    if sdk_body_class_name is not None and body_capture is not None:
        class _BodyRecorder:
            def __init__(self, **kwargs):
                body_capture.clear()
                body_capture.update(kwargs)
        setattr(akeyless_mod, sdk_body_class_name, _BodyRecorder)
    if extra_akeyless_attrs:
        for k, v in extra_akeyless_attrs.items():
            setattr(akeyless_mod, k, v)

    exc_mod = types.ModuleType("akeyless.exceptions")
    exc_mod.ApiException = FakeApiException
    akeyless_mod.exceptions = exc_mod
    sys.modules["akeyless"] = akeyless_mod
    sys.modules["akeyless.exceptions"] = exc_mod

    # Collection helpers under their canonical FQ names.
    for parent in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(parent, types.ModuleType(parent))
    for stem, path in (
        ("akeyless_lookup_auth", LOOKUP_AUTH_PATH),
        ("akeyless_plugin_helpers", PLUGIN_HELPERS_PATH),
    ):
        full = (
            f"ansible_collections.drzln0.akeyless.plugins.module_utils.{stem}"
        )
        sys.modules.pop(full, None)
        spec = importlib.util.spec_from_file_location(full, path)
        m = importlib.util.module_from_spec(spec)
        sys.modules[full] = m
        spec.loader.exec_module(m)


def load_lookup_module(lookup_filename: str, synthetic_name: str):
    """Load plugins/lookup/<filename>.py as a unique synthetic module."""
    path = REPO_ROOT / "plugins" / "lookup" / lookup_filename
    spec = importlib.util.spec_from_file_location(synthetic_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[synthetic_name] = mod
    spec.loader.exec_module(mod)
    return mod


SAVED_MODULE_KEYS = (
    "akeyless", "akeyless.exceptions", "ansible",
    "ansible.plugins", "ansible.plugins.lookup",
)


def snapshot_modules() -> Dict[str, Optional[Any]]:
    """Capture sys.modules entries the lookup stubs touch so a
    pytest fixture can restore them on teardown."""
    return {k: sys.modules.get(k) for k in SAVED_MODULE_KEYS}


def restore_modules(saved: Dict[str, Optional[Any]]) -> None:
    for k, v in saved.items():
        if v is None:
            sys.modules.pop(k, None)
        else:
            sys.modules[k] = v
