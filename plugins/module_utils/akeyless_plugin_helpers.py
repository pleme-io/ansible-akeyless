# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Decorator suite for Ansible plugins in this collection.

Sibling helpers:
  - akeyless_client.py       : module lifecycle helpers + SDK primitives.
  - akeyless_lookup_auth.py  : `authenticated_client(opts) -> (V2Api, token)`
                                shared by lookups + inventory.
  - akeyless_plugin_helpers.py (this file) : decorators that DRY repetitive
                                plugin boilerplate (lookups, filters,
                                tests, action plugins).

Why decorators here (vs. inheritance / mixins): each plugin type already
has an Ansible base class (LookupBase / FilterModule / TestModule /
ActionBase) and we don't want to fight Ansible's MRO. Decorators slot
between user code and the framework without disturbing inheritance.

Each decorator is independently importable, independently testable, and
preserves the wrapped callable's `__name__` / `__doc__` / `__module__`
via `functools.wraps`.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import functools
import inspect
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar

__all__ = [
    # Lookup-plugin decorators
    "akeyless_lookup",
    "AUTH_OPT_KEYS",
    # Filter-plugin decorators
    "akeyless_filter",
    # Test-plugin decorators
    "akeyless_test",
    # Utility helpers used by the decorators (exported for tests)
    "normalize_sdk_result",
    "compact_kwargs",
]

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# The canonical auth-option tuple every lookup / inventory plugin pulls
# from `self.get_option`. Pinned here so adding a new auth field is a
# one-place change.
AUTH_OPT_KEYS: Tuple[str, ...] = (
    "gateway_url",
    "access_id",
    "access_key",
    "access_type",
    "token",
)

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def normalize_sdk_result(result: Any) -> Any:
    """Akeyless SDK methods return model objects that expose a
    `.to_dict()` round-trip; older versions sometimes return a plain
    dict already. Normalise both into a plain Python value so callers
    don't have to branch."""
    if hasattr(result, "to_dict"):
        return result.to_dict()
    return result


def compact_kwargs(opts: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    """Pick `keys` out of `opts`, dropping any that are None or empty
    strings. Mirrors the per-lookup "only send the field if the user
    set it" idiom that was sprinkled across pki_certificate.py +
    every CRUD module's body construction.

    >>> compact_kwargs({"a": 1, "b": None, "c": ""}, ("a", "b", "c", "d"))
    {'a': 1}
    """
    return {k: opts[k] for k in keys if k in opts and opts[k] not in (None, "")}


# ---------------------------------------------------------------------------
# Lookup-plugin class decorator
# ---------------------------------------------------------------------------


def _lazy_imports():
    """Defer imports of ansible.errors + the auth helper so the module
    is importable in tests that don't have ansible-core installed."""
    from ansible.errors import AnsibleLookupError
    from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth import (
        authenticated_client,
    )
    try:
        from akeyless.exceptions import ApiException
    except ImportError:  # pragma: no cover - SDK absence handled upstream
        ApiException = Exception
    return AnsibleLookupError, authenticated_client, ApiException


def _wrap_api_exception(exc: Exception, label: str, AnsibleLookupError: Type[Exception]) -> Exception:
    """Standard ApiException -> AnsibleLookupError translation. Pulled
    out so subclasses can reuse the formatting when raising their own
    explicit lookup errors."""
    status = getattr(exc, "status", "?")
    body = getattr(exc, "body", None) or getattr(exc, "reason", "")
    return AnsibleLookupError(f"Akeyless {label} failed ({status}): {body}")


def akeyless_lookup(
    *,
    extra_opts: Sequence[str] = (),
    per_term: bool = True,
    fetch_method: str = "fetch",
) -> Callable[[type], type]:
    """Class decorator for `LookupBase` subclasses.

    Injects a `run(self, terms, variables=None, **kwargs)` method that:

      1. Calls `self.set_options(var_options=variables, direct=kwargs)`.
      2. Pulls AUTH_OPT_KEYS + extra_opts from self.get_option into an
         opts dict.
      3. Calls `authenticated_client(opts)` -> `(client, token)`.
      4. Dispatches to the user-supplied SDK call via `fetch_method`:
         - per_term=True:  invokes `getattr(self, fetch_method)(client,
           token, opts, term)` once per term, collecting results into
           a list.
         - per_term=False: invokes `getattr(self, fetch_method)(client,
           token, opts, terms)` once with all terms, expecting the
           method to return a list aligned to the input order.
      5. Translates `akeyless.exceptions.ApiException` to
         `AnsibleLookupError` with a uniform "Akeyless <call> failed
         (<status>): <body>" message.
      6. Normalises the per-term result via `normalize_sdk_result`
         (calls `.to_dict()` on SDK model objects).

    The decorated class is required to define a method matching
    `fetch_method` (default: `"fetch"`). Missing the method raises at
    decoration time -- the failure is at import, not at first lookup.

    Example (per-term):

        @akeyless_lookup(extra_opts=("common_name", "alt_names"))
        class LookupModule(LookupBase):
            def fetch(self, client, token, opts, term):
                body = akeyless.GetPKICertificate(
                    cert_issuer_name=term,
                    token=token,
                    **compact_kwargs(opts, ("common_name", "alt_names")),
                )
                return client.get_pki_certificate(body)

    Example (batch):

        @akeyless_lookup(per_term=False)
        class LookupModule(LookupBase):
            def fetch(self, client, token, opts, terms):
                body = akeyless.GetSecretValue(names=list(terms), token=token)
                result = client.get_secret_value(body)
                # batch-fetch returns dict; reshape to input-aligned list
                d = normalize_sdk_result(result)
                return [d[t] for t in terms]
    """
    all_opts: Tuple[str, ...] = (*AUTH_OPT_KEYS, *extra_opts)

    def class_decorator(cls: type) -> type:
        if not hasattr(cls, fetch_method):
            raise TypeError(
                f"@akeyless_lookup: class {cls.__name__} missing required "
                f"method `{fetch_method}(self, client, token, opts, "
                f"{'term' if per_term else 'terms'})`"
            )

        def run(self, terms: List[str], variables: Optional[Dict[str, Any]] = None,
                **kwargs: Any) -> List[Any]:
            AnsibleLookupError, authenticated_client, ApiException = _lazy_imports()
            self.set_options(var_options=variables, direct=kwargs)
            opts = {k: self.get_option(k) for k in all_opts}
            client, token = authenticated_client(opts)
            fetcher = getattr(self, fetch_method)

            if per_term:
                out: List[Any] = []
                for term in terms:
                    try:
                        result = fetcher(client, token, opts, term)
                    except ApiException as exc:
                        raise _wrap_api_exception(
                            exc, f"{fetcher.__name__}({term!r})",
                            AnsibleLookupError,
                        ) from exc
                    out.append(normalize_sdk_result(result))
                return out

            try:
                result = fetcher(client, token, opts, terms)
            except ApiException as exc:
                raise _wrap_api_exception(
                    exc, fetcher.__name__, AnsibleLookupError,
                ) from exc
            return result if isinstance(result, list) else [normalize_sdk_result(result)]

        run.__qualname__ = f"{cls.__name__}.run"
        cls.run = run
        return cls

    return class_decorator


# ---------------------------------------------------------------------------
# Filter-plugin function decorator
# ---------------------------------------------------------------------------


def akeyless_filter(
    fn: Optional[F] = None,
    *,
    expects: type = str,
    label: Optional[str] = None,
) -> F:
    """Decorator for Jinja2 filter functions.

    Enforces two invariants every Akeyless filter shares:

      1. The first argument must be `isinstance(_, expects)` (default
         `str`). Wrong type -> raise AnsibleFilterError with a uniform
         "<filter_name> expects <type>, got <actual>" message.
      2. Any exception other than AnsibleFilterError raised by the
         wrapped function is translated to AnsibleFilterError with
         a "<filter_name> failed: <exc>" message, preserving the
         chain via `raise ... from exc`.

    Supports both `@akeyless_filter` and `@akeyless_filter(expects=dict)`
    forms.
    """
    # Friendlier type-name display: "string" not "str", "dictionary"
    # not "dict". Falls back to __name__ for everything else.
    _TYPE_DISPLAY = {str: "string", dict: "dictionary", list: "list",
                     int: "integer", float: "number", bool: "boolean"}

    def deco(f: F) -> F:
        # Import lazily so tests don't need ansible.errors at module load.
        @functools.wraps(f)
        def wrapped(value: Any, *args: Any, **kwargs: Any) -> Any:
            from ansible.errors import AnsibleFilterError
            name = label or f.__name__
            if not isinstance(value, expects):
                expected_name = _TYPE_DISPLAY.get(expects, expects.__name__)
                raise AnsibleFilterError(
                    f"{name} expects a {expected_name}, got "
                    f"{type(value).__name__}"
                )
            try:
                return f(value, *args, **kwargs)
            except AnsibleFilterError:
                raise
            except Exception as exc:
                raise AnsibleFilterError(f"{name} failed: {exc}") from exc
        return wrapped  # type: ignore[return-value]

    # @akeyless_filter (no parens) form
    if fn is not None and callable(fn):
        return deco(fn)
    return deco  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Test-plugin function decorator
# ---------------------------------------------------------------------------


def akeyless_test(
    fn: Optional[F] = None,
    *,
    requires_string: bool = True,
) -> F:
    """Decorator for Jinja2 test functions.

    Tests are predicates; they MUST return True/False and MUST NOT
    raise. The collection's tests share two behaviours:

      1. When `requires_string=True` (default), a non-string input
         returns False immediately. Saves every test from spelling
         the `if not isinstance(value, str): return False` guard.
      2. Any exception bubbling out of the wrapped predicate is
         interpreted as "the value doesn't satisfy the predicate"
         and returns False -- never raises, never lets Jinja's
         render fail on a malformed value.

    Supports both `@akeyless_test` and `@akeyless_test(requires_string=False)`
    forms.
    """
    def deco(f: F) -> F:
        @functools.wraps(f)
        def wrapped(value: Any, *args: Any, **kwargs: Any) -> bool:
            if requires_string and not isinstance(value, str):
                return False
            try:
                return bool(f(value, *args, **kwargs))
            except Exception:
                return False
        return wrapped  # type: ignore[return-value]

    if fn is not None and callable(fn):
        return deco(fn)
    return deco  # type: ignore[return-value]
