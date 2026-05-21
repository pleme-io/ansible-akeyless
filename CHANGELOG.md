# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (placeholder for next release)

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
