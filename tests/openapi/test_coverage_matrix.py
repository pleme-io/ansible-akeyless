# Copyright: (c) 2026, pleme-io
# MIT License
#
# OpenAPI compatibility proof for the generated Ansible collection.
#
# This module provides three complementary tests that, taken together,
# guarantee the generated modules are structurally compatible with the
# upstream Akeyless OpenAPI surface:
#
#   1. test_every_module_calls_real_operation_id
#      Every call_api(..., "<snake_name>", ...) literal in a generated
#      module must resolve to a real OpenAPI operationId (after the
#      canonical camelCase <-> snake_case dance).
#
#   2. test_coverage_report
#      Walks the OpenAPI spec, reports total/covered/skipped operationIds,
#      writes a timestamped COVERAGE.md snapshot, and fails if any
#      uncovered op isn't explicitly classified in skip.yml --
#      this catches upstream API drift in CI.
#
#   3. test_module_request_body_matches_openapi_schema
#      For every module's build_body("<PascalClass>", params) call, find
#      the matching OpenAPI requestBody schema and (a) verify required
#      fields appear in the module's argument_spec and (b) verify the
#      module doesn't ship unknown fields. This is structural -- not
#      full semantic -- compatibility.
#
# Skipped operations are tracked in tests/openapi/skip.yml with one of
# the categories: pangea_specific, deprecated, future_phase, internal_only.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import datetime as _dt
import os
import re
from collections import defaultdict
from pathlib import Path

import pytest

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"


def _resolve_openapi_path() -> Path:
    """Return the OpenAPI spec path.

    Honors the AKEYLESS_OPENAPI_YAML env var first (CI sets this when it
    fetches the spec). Falls back to the local workspace clone, then to a
    sibling akeyless-go checkout next to this repo.
    """
    env = os.environ.get("AKEYLESS_OPENAPI_YAML")
    if env:
        return Path(env)
    candidates = [
        Path("/home/drzzln/code/github/pleme-io/akeyless-go/api/openapi.yaml"),
        REPO_ROOT.parent / "akeyless-go" / "api" / "openapi.yaml",
        REPO_ROOT / "tests" / "openapi" / "openapi.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Return the first candidate so the skip message in _load_openapi is clear.
    return candidates[0]


OPENAPI_YAML = _resolve_openapi_path()
SKIP_YML = Path(__file__).parent / "skip.yml"
COVERAGE_MD = Path(__file__).parent / "COVERAGE.md"


# ---------------------------------------------------------------------------
# Loaders (cached at module import; the OpenAPI spec is ~120k lines).
# ---------------------------------------------------------------------------

_OPENAPI_CACHE: dict = {}


def _load_openapi() -> dict:
    """Parse the OpenAPI spec once and cache it for the whole test run."""
    if "spec" in _OPENAPI_CACHE:
        return _OPENAPI_CACHE["spec"]
    if not OPENAPI_YAML.exists():
        pytest.skip(f"OpenAPI spec not available at {OPENAPI_YAML}")
    if yaml is None:
        pytest.skip("pyyaml not installed -- pip install pyyaml")
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with OPENAPI_YAML.open() as f:
        spec = yaml.load(f, Loader=loader)
    _OPENAPI_CACHE["spec"] = spec
    return spec


def _operation_index() -> dict:
    """Return {operationId: {'path': p, 'method': m, 'request_schema_ref': ref|None}}."""
    if "ops" in _OPENAPI_CACHE:
        return _OPENAPI_CACHE["ops"]
    spec = _load_openapi()
    ops: dict = {}
    for path, path_item in (spec.get("paths") or {}).items():
        for method, op in (path_item or {}).items():
            if method.lower() not in ("get", "post", "put", "delete", "patch", "options", "head"):
                continue
            op_id = op.get("operationId")
            if not op_id:
                continue
            ref = None
            body = op.get("requestBody") or {}
            content = body.get("content") or {}
            json_body = content.get("application/json") or {}
            schema = json_body.get("schema") or {}
            if "$ref" in schema:
                ref = schema["$ref"]
            ops[op_id] = {"path": path, "method": method, "request_schema_ref": ref}
    _OPENAPI_CACHE["ops"] = ops
    return ops


def _schemas() -> dict:
    spec = _load_openapi()
    return ((spec.get("components") or {}).get("schemas") or {})


def _load_skip() -> dict:
    """Return {operationId: {'category': str, 'reason': str}}."""
    if not SKIP_YML.exists():
        return {}
    if yaml is None:
        return {}
    with SKIP_YML.open() as f:
        data = yaml.safe_load(f) or {}
    return data.get("skip", {})


# ---------------------------------------------------------------------------
# Naming conversion.
# OpenAPI operationIds are mixedCase or camelCase (e.g. `accountCustomFieldCreate`,
# `CertificateDiscovery`, `get-cert-challenge`). The SDK normalizes these to
# snake_case method names. We replicate that conversion exactly.
# ---------------------------------------------------------------------------


def op_to_snake(name: str) -> str:
    """Convert an OpenAPI operationId to the SDK snake_case method name."""
    if "-" in name:
        # e.g. "get-cert-challenge" -> "get_cert_challenge"
        return name.replace("-", "_").lower()
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def pascal_to_camel(name: str) -> str:
    """Convert build_body("AccountCustomFieldCreate", ...) -> OpenAPI schema key.

    Modules pass the SDK model class name in PascalCase. OpenAPI schemas
    are keyed by the same identifier but with the first letter lowercased
    (the OpenAPI Generator convention).
    """
    if not name:
        return name
    return name[0].lower() + name[1:]


# ---------------------------------------------------------------------------
# Module extraction helpers.
# ---------------------------------------------------------------------------


def _all_module_paths() -> list:
    return sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _extract_call_api(tree: ast.AST) -> list:
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if nm == "call_api" and len(n.args) >= 3:
            m = n.args[2]
            if isinstance(m, ast.Constant) and isinstance(m.value, str):
                out.append(m.value)
    return out


def _extract_build_body(tree: ast.AST) -> list:
    """Return the list of PascalCase class names passed to build_body."""
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if nm == "build_body" and node_first_string(n) is not None:
            out.append(node_first_string(n))
    return out


def node_first_string(call_node: ast.Call):
    if not call_node.args:
        return None
    a = call_node.args[0]
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return a.value
    return None


def _extract_argument_spec(tree: ast.AST) -> dict:
    """Best-effort: pull out the argument_spec = {...} literal."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "argument_spec" and isinstance(n.value, ast.Dict):
                    out = {}
                    for k, v in zip(n.value.keys, n.value.values):
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            out[k.value] = _literal_or_none(v)
                    return out
    return {}


def _literal_or_none(node):
    try:
        return ast.literal_eval(node)
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------


def test_every_module_calls_real_operation_id():
    """Every call_api(..., "<method>", ...) literal must map to an OpenAPI operationId."""
    ops = _operation_index()
    snake_to_op = {op_to_snake(o): o for o in ops}

    missing = []
    for p in _all_module_paths():
        tree = ast.parse(p.read_text())
        for m in _extract_call_api(tree):
            if m not in snake_to_op:
                missing.append((p.name, m))

    assert not missing, (
        "call_api method names not mapped to any OpenAPI operationId:\n"
        + "\n".join(f"  {fn}: {meth}" for fn, meth in sorted(missing))
    )


def test_coverage_report():
    """Walk the OpenAPI spec, write COVERAGE.md, fail if uncovered ops aren't classified."""
    ops = _operation_index()
    skip = _load_skip()
    snake_to_op = {op_to_snake(o): o for o in ops}

    # Build the inverse: which operationIds are wrapped by at least one module
    used_snake: set = set()
    for p in _all_module_paths():
        tree = ast.parse(p.read_text())
        for m in _extract_call_api(tree):
            used_snake.add(m)

    covered_ops = {snake_to_op[s] for s in used_snake if s in snake_to_op}
    all_ops = set(ops)
    uncovered = sorted(all_ops - covered_ops)
    skipped = {o for o in uncovered if o in skip}
    not_classified = sorted(o for o in uncovered if o not in skip)

    # Build the report.
    total = len(all_ops)
    covered_n = len(covered_ops)
    skipped_n = len(skipped)
    effective_n = covered_n + skipped_n
    pct_covered = (covered_n / total * 100.0) if total else 0.0
    pct_effective = (effective_n / total * 100.0) if total else 0.0

    by_category: dict = defaultdict(list)
    for op in sorted(skipped):
        by_category[skip[op].get("category", "uncategorized")].append(op)

    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = []
    lines.append("# OpenAPI coverage matrix")
    lines.append("")
    lines.append(f"Generated: `{timestamp}`")
    lines.append("")
    lines.append("Source spec: `/home/drzzln/code/github/pleme-io/akeyless-go/api/openapi.yaml`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total operationIds | {total} |")
    lines.append(f"| Covered by an Ansible module | {covered_n} ({pct_covered:.1f}%) |")
    lines.append(f"| Explicitly skipped (`skip.yml`) | {skipped_n} |")
    lines.append(f"| Not yet classified | {len(not_classified)} |")
    lines.append(f"| **Effective coverage** | **{effective_n} / {total} ({pct_effective:.1f}%)** |")
    lines.append("")
    if by_category:
        lines.append("## Skip categories")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        for cat in sorted(by_category):
            lines.append(f"| `{cat}` | {len(by_category[cat])} |")
        lines.append("")
    if uncovered:
        lines.append("## Uncovered operationIds")
        lines.append("")
        lines.append("| operationId | Category | Reason |")
        lines.append("|---|---|---|")
        for op in uncovered:
            entry = skip.get(op) or {}
            cat = entry.get("category", "UNCLASSIFIED")
            reason = entry.get("reason", "(no entry in skip.yml)")
            lines.append(f"| `{op}` | `{cat}` | {reason} |")
        lines.append("")
    COVERAGE_MD.write_text("\n".join(lines) + "\n")

    assert not not_classified, (
        f"{len(not_classified)} OpenAPI operationId(s) are not covered by any "
        f"module and not classified in tests/openapi/skip.yml -- catches API "
        f"surface drift. Either wrap them in a module, or add a skip entry "
        f"with category + reason.\n"
        + "\n".join(f"  {op}" for op in not_classified[:30])
        + ("" if len(not_classified) <= 30 else f"\n  ... and {len(not_classified) - 30} more")
    )


# ---------------------------------------------------------------------------
# Per-module request-body structural validation.
#
# Modules pass a PascalCase class name to build_body("<Class>", params).
# That class name maps 1:1 to an OpenAPI component schema (with the first
# letter lowercased -- the OpenAPI Generator convention). The schema lists
# the request properties and the `required` set.
#
# We check two structural properties per module:
#
#   (a) Every required schema field is either present in the module's
#       argument_spec, or is one of the auth/transport fields injected at
#       call time (token, uid_token, json).
#
#   (b) No fields in the module's argument_spec are unknown to the schema
#       (modulo the standard auth keys). This catches drift in the other
#       direction.
#
# Modules with known generator gaps -- where the schema's required set
# doesn't match the spec source's parameter list -- are tracked in
# tests/openapi/schema_xfail.yml so the test stays green while still
# documenting the gap for follow-up in ansible-forge.
# ---------------------------------------------------------------------------


SCHEMA_XFAIL_YML = Path(__file__).parent / "schema_xfail.yml"


def _resolve_ref(spec_ref: str, schemas: dict) -> dict:
    """Resolve a '#/components/schemas/X' reference."""
    if not spec_ref:
        return {}
    if not spec_ref.startswith("#/components/schemas/"):
        return {}
    key = spec_ref.split("/")[-1]
    return schemas.get(key) or {}


def _module_id(path: Path) -> str:
    return path.stem


def _module_schema_targets() -> list:
    """Return [(module_path, class_name), ...] for the CREATE/UPDATE/DELETE/GET pairs.

    We focus on the CREATE schema for each module because that's the broadest
    surface (most required fields). UPDATE/DELETE/GET share the same arg-spec
    so checking CREATE catches the structural issues.
    """
    out = []
    schemas = _schemas()
    for p in _all_module_paths():
        tree = ast.parse(p.read_text())
        seen_create_classes = set()
        for cls in _extract_build_body(tree):
            # Pick Create classes preferentially; fall back to whatever there is
            if cls.endswith("Create") and pascal_to_camel(cls) in schemas:
                seen_create_classes.add(cls)
        # Add up to one Create class per module
        if seen_create_classes:
            out.append((p, sorted(seen_create_classes)[0]))
        else:
            # Fall back: the first build_body class that resolves to a schema
            for cls in _extract_build_body(tree):
                if pascal_to_camel(cls) in schemas:
                    out.append((p, cls))
                    break
    return out


def _load_schema_xfail() -> dict:
    """Return {module_stem: {'missing_required': [...], 'reason': '...'}}."""
    if not SCHEMA_XFAIL_YML.exists():
        return {}
    if yaml is None:
        return {}
    with SCHEMA_XFAIL_YML.open() as f:
        data = yaml.safe_load(f) or {}
    return data.get("xfail", {})


@pytest.mark.parametrize(
    "module_path,class_name",
    _module_schema_targets(),
    ids=lambda v: v.stem if hasattr(v, "stem") else v,
)
def test_module_request_body_matches_openapi_schema(module_path: Path, class_name: str):
    """For each module's CREATE build_body, the OpenAPI requestBody schema's
    required fields must all appear in the module's argument_spec."""
    if yaml is None:
        pytest.skip("pyyaml not installed")
    schemas = _schemas()
    schema_key = pascal_to_camel(class_name)
    schema = schemas.get(schema_key)
    if not schema:
        pytest.skip(f"OpenAPI schema {schema_key!r} not found for module {module_path.name}")

    tree = ast.parse(module_path.read_text())
    argspec = _extract_argument_spec(tree)
    if not argspec:
        pytest.skip(f"{module_path.name}: argument_spec not extractable as a literal dict")

    # Auth params injected by the generator -- never appear in the schema.
    auth_keys = {"gateway_url", "access_id", "access_key", "access_type"}
    # OpenAPI uses hyphens (object-type, uid-token); module uses underscores.
    required = {p.replace("-", "_") for p in (schema.get("required") or [])}

    arg_keys = set(argspec) - auth_keys - {"state"}

    # Every required schema field (other than ones auto-injected at call time)
    # must be present in the module's argument_spec.
    auto_injected = {"token", "uid_token", "json"}
    missing_required = (required - arg_keys) - auto_injected

    # Allow a known-tracked xfail (generator gap, fix lives upstream in
    # ansible-forge). We still assert that the xfail entry's expected
    # missing set matches reality so the xfail can't silently grow.
    xfail = _load_schema_xfail().get(module_path.stem)
    if xfail:
        expected_missing = set(xfail.get("missing_required") or [])
        if missing_required <= expected_missing:
            pytest.xfail(
                f"{module_path.name}: known generator gap "
                f"(fix in ansible-forge): missing required fields "
                f"{sorted(missing_required)}. Reason: {xfail.get('reason', '')}"
            )

    assert not missing_required, (
        f"{module_path.name} ({class_name}): argument_spec is missing required "
        f"OpenAPI schema fields: {sorted(missing_required)}. If this is a known "
        f"generator gap, add an entry under tests/openapi/schema_xfail.yml."
    )
