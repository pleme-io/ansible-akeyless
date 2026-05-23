# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Galaxy namespace moved from `akeyless` to `drzln0`.** Galaxy's `akeyless`
  namespace is owned by another publisher, so we publish under the
  user-controlled `drzln0` account (auto-created when `drzln` was
  unavailable). All generated module imports now resolve via
  `ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client`;
  every example playbook, the `flake.nix` collection wrapper, the docs
  workflow, the release tarball pattern, and the in-repo tests have been
  updated to match. Users must migrate via
  `ansible-galaxy collection install drzln0.akeyless` and update playbook
  references from `akeyless.akeyless.<module>` to `drzln0.akeyless.<module>`.
- The namespace is now data-driven: ansible-forge reads
  `[platforms.ansible] galaxy_namespace` from `provider.toml` and threads
  it through `generate_resource_module`, `generate_data_source_module`,
  and `generate_action_module`. No more hardcoded `"akeyless"` string in
  the generator.

## [0.2.x] — 2026-05-23 (in-flight)

Substantial expansion of the non-module Ansible Galaxy surface and
generator-side hardening. Galaxy publishes catching up across tags
v0.2.6+ as CI blockers clear.

### Added — non-module Galaxy plugin types

- **Inventory plugin** `drzln0.akeyless.akeyless` — loads hosts from
  JSON-shaped static secrets. Addresses PRM-1767 (Pepsico's
  "we don't want to rewrite every play with lookup calls" request):
  teams add Akeyless as an inventory source in AWX/AAP, then
  playbooks reference values via standard `host_vars` / `group_vars`.
- **Lookup plugins** (+2): `dynamic_secret`, `pki_certificate`. Both
  follow the existing `secret` lookup's auth + exception-chaining
  patterns.
- **Filter plugins** (7 total): `b64decode_secret` (strict-validate),
  `parse_dotenv_secret`, `secret_to_json`, `split_pem_bundle`,
  `secret_keys_to_env`, `mask_secret`, `secret_strength`
  (Shannon entropy + classification).
- **Test plugins** (4): `is_akeyless_path`, `is_akeyless_access_id`,
  `is_pem_block`, `is_base64` — one file per test for ansible-doc
  compatibility.
- **Callback plugin** `akeyless_redactor` — defensive secondary-pass
  secret redaction in task result rendering.
- **Action plugin** `secret_to_file` — atomically fetches a secret
  and writes it to a remote file. Secret value never appears in
  task-arg rendering.
- **Cache plugin** `akeyless_token` — file-backed token cache
  (0600 perms, atomic writes, TTL, self-healing) to skip per-play
  re-auth.
- **Roles** (2): `akeyless_bootstrap`, `akeyless_install_certificate`.
- **Playbooks** (2): `fetch_secrets_into_env_file.yml`,
  `install_certificate_with_defaults.yml`.

### Added — collection metadata

- `meta/runtime.yml` `action_groups.all` with all 209 module names.
  Users can now set Akeyless auth ONCE via
  `module_defaults: group/drzln0.akeyless.all:` instead of repeating
  on every task.
- `plugins/module_utils/akeyless_lookup_auth.py` — shared auth
  helper (DRY -150 LOC across 4 callers).

### Added — Python craft on the helper

- Typed exception hierarchy: `AkeylessError` + `AkeylessConfigError` /
  `AkeylessSdkError` / `AkeylessAuthError` / `AkeylessApiError`
  carrying `status` + `details`.
- `AkeylessConfig` frozen dataclass, `HttpStatus(IntEnum)`,
  `AnsibleModuleLike` Protocol, `@requires_sdk` decorator,
  `functools.cache` modernization, `Final[str]` constants, full type
  annotations.
- `_did_you_mean` difflib suggestions on unknown-model / unknown-method
  paths.

### Added — tests + CI

- **+4000 unit/mock/sanity test cases** (1541 → 5890): module-load
  sweeps, license-header sweeps, YAML-block validation, import-
  discipline, action-shadow coherence, coverage threshold, FQCN
  convention, plugin-load sweep, cache property tests.
- Hypothesis property tests: 17 classes, ~1500 random examples.
- New CI workflows: `coverage-matrix.yml` (Py 3.10–3.13 fan-out
  with pytest-cov), `ansible-lint.yml`.
- Cross-repo prime-directive backstop now byte-exact checks
  `meta/runtime.yml` + helper + every module.

### Resolved

- 471 integration playbooks rewritten from bare → FQCN.
- Generator-side `\"...\"` escape bug in OpenAPI descriptions.
- Lookup auth duplication consolidated.

## [0.2.0] — 2026-05-21

First fully-working baseline. The collection moves from "TODO-stub scaffolding" to **208 working modules** that wrap the Akeyless V2 API via the `akeyless` Python SDK.

### Added

- **157 CRUD resource modules** covering auth methods (16), roles (3), static + dynamic + rotated secrets (56), targets (29), keys (4), gateway producers (24), log forwarding (10), KMIP (2), and miscellaneous resources.
- **25 `_info` data-source modules** for read-only list / get endpoints.
- **26 RPC action modules** for non-CRUD endpoints: UID token operations (5), crypto (12 — encrypt/decrypt/sign/verify/hmac/derive_key + batch variants), certificate lifecycle (7), rotated-secret sync (2).
- Shared `plugins/module_utils/akeyless_client.py` helper: single auth touch-point, request-body construction, response masking, 404-tolerant reads.
- Collection metadata: `galaxy.yml`, `meta/runtime.yml`, `requirements.txt`, `README.md`.
- `tests/sanity/smoke.py` — AST-based structural and SDK-binding sanity check.
- `tests/unit/` — pytest suite: helper unit tests, parametrised shape tests across all 208 modules, behaviour tests for representative CRUD / action / info modules.
- `.github/workflows/ci.yml` — runs smoke + pytest on push and pull requests.

### Resolved

- **PRM-1790**: Universal Identity token operations (`uid_generate_token`, `uid_rotate_token`, `uid_create_child_token`, `uid_list_children`, `uid_revoke_token`) are first-class action modules with `token` masked in the result.
- Replaces the original 119 modules that contained only `# TODO: implement API call` stubs.

### Notes

- 25 of the gateway producer modules wrap endpoints flagged deprecated upstream (use `dynamic_secret_*` instead). The deprecation note is included in each module's `description`.
- Integration test playbooks under `tests/integration/targets/*/` exercise the module entry point but do not validate against a live Akeyless instance. Live-endpoint integration coverage is tracked as a follow-up.

### Generator chain at this release

| Repo | Commit |
|---|---|
| `akeyless-terraform-resources` | `9d6f729` (183 TOML specs) |
| `iac-forge` | `4d774664` (`read_mapping` IR + `IacAction`) |
| `ansible-forge` | `98379a1` (real SDK emission + action emitter + snapshot + TOML-walk tests) |
| `iac-forge-cli` | `69bfd74` (action dispatch) |

[Unreleased]: https://github.com/pleme-io/ansible-akeyless/compare/v0.2-full-api...HEAD
[0.2.0]: https://github.com/pleme-io/ansible-akeyless/releases/tag/v0.2-full-api
