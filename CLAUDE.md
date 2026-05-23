# Ansible-Akeyless

> **★★★ CSE / Knowable Construction.** This repo operates under **Constructive Substrate Engineering** — canonical specification at [`pleme-io/theory/CONSTRUCTIVE-SUBSTRATE-ENGINEERING.md`](https://github.com/pleme-io/theory/blob/main/CONSTRUCTIVE-SUBSTRATE-ENGINEERING.md). The Compounding Directive (operational rules: solve once, load-bearing fixes only, idiom-first, models stay current, direction beats velocity) is in the org-level pleme-io/CLAUDE.md ★★★ section. Read both before non-trivial changes.

## What this is

`drzln0.akeyless` is an auto-generated Ansible Collection wrapping the entire
Akeyless V2 API (208 modules, 378 SDK methods at 100% coverage). The
collection is published to Ansible Galaxy and the source-of-truth is the
[`ansible-forge`](https://github.com/pleme-io/ansible-forge) generator
reading [`akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources)
TOML specs.

## Prime directive (load-bearing)

Three pieces, three commits when the helper shape changes:

```
akeyless-terraform-resources    →    ansible-forge          →    ansible-akeyless
(TOML specs + provider.toml)         (generator templates)        (this repo, published)
```

If you change the helper architecture (`plugins/module_utils/akeyless_client.py`):

1. Update the helper here. Tests under `tests/unit/plugins/module_utils/`
   pin the public API surface (`test_public_api.py`) and behaviour
   (`test_lifecycle_helpers.py`).
2. **Sync the same change into `ansible-forge/src/client_helper.py`** —
   this is the source-of-truth that `iac-forge generate --backend ansible`
   bundles into every regenerated collection. The
   `tests/integration_regen_matches_collection.rs` backstop in ansible-forge
   catches drift via a byte-exact compare. Skipping this step is a
   prime-directive violation: the next regen wipes your downstream change.
3. If the change affects per-module emission (templates, not the helper),
   update `ansible-forge/src/module_gen.rs` and its tests.

## Pipeline architecture

- `pleme-io/actions/substrate-bump@v1` increments patch on every push that
  touches `plugins/` / `meta/` / `galaxy.yml`. Test-only commits (under
  `tests/`) intentionally don't bump — nothing functional to ship.
- Manual minor bumps: edit `galaxy.yml` `version:` directly; substrate-bump
  picks up from there next push.
- Release flow: push → auto-bump → tag → release.yml → Galaxy publish
  (~4-minute cycle).

## Test pyramid (every PR must pass)

`nix flake check` runs (declared in flake.nix):

- **smoke** — `tests/sanity/smoke.py`: AST sweep, 208/208 modules,
  100% SDK method coverage check.
- **unit** — `tests/unit/`: ~4500 cases including module-shape sweeps,
  load sweeps, license-header sweeps, YAML-block sweeps, lifecycle helper
  behaviour + property tests.
- **mock** — `tests/mock/`: SDK-mocked module main() invocations.
- **sanity** — `tests/sanity/` (excl. smoke): galaxy.yml + meta + doc
  fragments + integration playbook YAML invariants.
- **openapi** — `tests/openapi/`: live OpenAPI coverage check.

Additional CI: ansible-test sanity, CodeQL, docs-lint, integration-live
(real Akeyless gateway), matrix coverage, published-install.

## Helper module public API

`plugins/module_utils/akeyless_client.py` exports (pinned via `__all__`):

- **Lifecycle helpers** (decorated with `@lifecycle_helper`):
  `run_standard_crud`, `run_action_module`, `run_info_module`.
- **Primitives**: `get_client`, `call_api`, `build_body`.
- **Idempotency**: `compute_diff`, `drift_to_diff`, `IDEMPOTENCY_IGNORE_KEYS`.
- **Typed value objects**: `SdkCall(NamedTuple)`.
- **Decorators / registries**: `lifecycle_helper`, `LIFECYCLE_HELPERS`,
  `PRIMITIVES`.
- **Constants**: `DEFAULT_GATEWAY_URL`, `DEFAULT_ACCESS_TYPE`,
  `HAS_AKEYLESS`, `AKEYLESS_IMPORT_ERROR`.

Adding a public symbol = update `__all__` + `EXPECTED_*` sets in
`tests/unit/plugins/module_utils/test_public_api.py`. A deliberate
two-place edit that's hard to do by accident.
