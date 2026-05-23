# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep: every drzln0.akeyless.<module> reference in any
# tests/integration/targets/**/*.yml file must resolve to an actual
# plugins/modules/<module>.py file. Catches:
#   - typo'd module names in a freshly-generated integration target
#     (`role_assoc` instead of `role_auth_method_assoc`)
#   - integration targets that lag behind a module rename / deletion
#
# Complements the YAML-parse sanity (test_integration_playbooks_parse)
# which only checks shape, not module-name validity.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
INTEGRATION_DIR = REPO_ROOT / "tests" / "integration" / "targets"

# Match the FQCN form on a task `module:` line OR as a module type
# header (e.g. `drzln0.akeyless.role:`). The first capture group is
# the module name.
_FQCN_RE = re.compile(
    r"\bdrzln0\.akeyless\.([a-z][a-z0-9_]+)\s*:",
)


def _existing_module_stems() -> set:
    return {
        p.stem for p in MODULES_DIR.glob("*.py")
        if p.name != "__init__.py"
    }


def _integration_yaml_files():
    if not INTEGRATION_DIR.exists():
        return []
    return sorted(INTEGRATION_DIR.rglob("*.yml")) + sorted(INTEGRATION_DIR.rglob("*.yaml"))


MODULE_STEMS = _existing_module_stems()
YAML_FILES = _integration_yaml_files()


def _collect_referenced_modules(text: str) -> set:
    """Pull out every drzln0.akeyless.<name>: reference. We don't
    distinguish module references from plugin references (filters /
    lookups / tests use the same FQCN pattern), so we'll allow names
    that match either a module or a known plugin."""
    return set(_FQCN_RE.findall(text))


# Known non-module plugins that ALSO appear with the
# `drzln0.akeyless.<name>:` shape in integration playbooks.
_KNOWN_NON_MODULE_NAMES = frozenset({
    # Lookups (used as `lookup('drzln0.akeyless.<name>', ...)` --
    # appears with quotes around it, not the bare `:`, but our regex
    # is permissive so allow these too)
    "secret", "dynamic_secret", "pki_certificate",
    # Roles (used as `role: drzln0.akeyless.<name>`)
    "akeyless_bootstrap", "akeyless_install_certificate",
    # Action plugin (also has a module shadow but we list defensively)
    "secret_to_file",
    # Filters / tests (referenced in expressions, our regex might
    # catch some shapes)
    "b64decode_secret", "parse_dotenv_secret", "secret_to_json",
    "split_pem_bundle", "secret_keys_to_env", "mask_secret",
    "secret_strength",
    "is_akeyless_path", "is_akeyless_access_id",
    "is_pem_block", "is_base64",
})


@pytest.mark.parametrize(
    "yaml_path",
    YAML_FILES,
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_referenced_modules_exist(yaml_path):
    """Every drzln0.akeyless.<name>: reference in this YAML must
    resolve to either an actual module file OR a known non-module
    plugin name. Unknown names fail loudly."""
    text = yaml_path.read_text()
    referenced = _collect_referenced_modules(text)
    if not referenced:
        pytest.skip("no drzln0.akeyless.* references in this file")
    unknown = referenced - MODULE_STEMS - _KNOWN_NON_MODULE_NAMES
    assert not unknown, (
        f"{yaml_path.relative_to(REPO_ROOT)} references unknown "
        f"drzln0.akeyless.* names: {sorted(unknown)}. Likely typos OR "
        f"references to modules that don't exist (deleted? renamed?)."
    )
