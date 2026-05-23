# Architecture

How the helper, the plugin decorator suite, and the per-plugin layout
fit together. Read this if you're contributing to the collection or
trying to debug why something behaves the way it does.

## The prime directive (lockstep with two upstream repos)

Three repos move together:

```
akeyless-terraform-resources  →  ansible-forge  →  ansible-akeyless
(TOML specs + provider.toml)     (Rust generator)    (this repo, published)
```

- **akeyless-terraform-resources** holds 119 TOML specs describing
  each Akeyless V2 resource (auth methods, secrets, targets, etc).
  Source of truth for what modules exist.
- **ansible-forge** is the Rust generator. Reads the TOMLs, emits
  the 209 Python modules under `plugins/modules/`. Also bundles
  `client_helper.py` (which becomes
  `plugins/module_utils/akeyless_client.py` here).
- **ansible-akeyless** is what this repo ships to Galaxy. Modules
  are regenerated; the hand-written non-module plugins
  (lookup / inventory / filter / test / callback / action / cache)
  live in `plugins/<type>/` and are NOT regenerated.

A backstop in ansible-forge byte-compares the regen output against
this repo on every PR. Skipping the sync in either direction fails
that backstop.

## The two helper modules

`plugins/module_utils/akeyless_client.py` is the load-bearing helper
for modules. It exports (pinned via `__all__`):

- **Lifecycle helpers**: `run_standard_crud`, `run_action_module`,
  `run_info_module`. Every generated module's `main()` calls exactly
  one of these.
- **Primitives**: `get_client`, `call_api`, `build_body`.
- **Idempotency**: `compute_diff`, `drift_to_diff`,
  `IDEMPOTENCY_IGNORE_KEYS`.
- **Typed value objects**: `SdkCall` NamedTuple, `AkeylessConfig`
  frozen dataclass, `HttpStatus` IntEnum, `AnsibleModuleLike`
  Protocol.
- **Exception hierarchy**: `AkeylessError` + `AkeylessConfigError` /
  `AkeylessSdkError` / `AkeylessAuthError` / `AkeylessApiError`,
  each carrying `status` + `details`.
- **Decorators / registries**: `lifecycle_helper`, `requires_sdk`,
  `LIFECYCLE_HELPERS`, `PRIMITIVES`.
- **Constants**: `DEFAULT_GATEWAY_URL`, `DEFAULT_ACCESS_TYPE`,
  `HAS_AKEYLESS`, `AKEYLESS_IMPORT_ERROR`.

`plugins/module_utils/akeyless_plugin_helpers.py` is the
hand-written-plugin equivalent. It exports the three decorators
that DRY the lookup / filter / test plugin boilerplate:

- **`@akeyless_lookup`** — class decorator for `LookupBase` subclasses.
  Injects the standard `run()` that does set_options + auth +
  per-term loop + ApiException translation + `.to_dict()`
  normalisation. The decorated class only defines `fetch()`.
- **`@akeyless_filter`** — function decorator for filters. Strict
  type-check + uniform `AnsibleFilterError` translation.
- **`@akeyless_test`** — function decorator for tests. Non-string
  input → `False`; predicate exception → `False`.
- **Utility helpers**: `AUTH_OPT_KEYS`, `normalize_sdk_result`,
  `compact_kwargs`.

The third helper is `plugins/module_utils/akeyless_lookup_auth.py`:
one function (`authenticated_client(opts) -> (V2Api, token)`)
that the `@akeyless_lookup` decorator + the inventory plugin call.

## Per-plugin layout

```
plugins/
├── modules/                  (209 auto-generated)
├── module_utils/
│   ├── akeyless_client.py             (lifecycle helpers, primitives)
│   ├── akeyless_lookup_auth.py        (authenticated_client)
│   └── akeyless_plugin_helpers.py     (decorator suite)
├── lookup/                  (3 wire-decorated)
│   ├── secret.py
│   ├── dynamic_secret.py
│   └── pki_certificate.py
├── inventory/               (1)
│   └── akeyless.py
├── filter/                  (1 shared impl + 7 per-filter wrappers)
│   ├── akeyless.py          (impl, FilterModule with all 7)
│   ├── b64decode_secret.py  (wrapper with own DOCUMENTATION)
│   ├── parse_dotenv_secret.py
│   ├── secret_to_json.py
│   ├── split_pem_bundle.py
│   ├── secret_keys_to_env.py
│   ├── mask_secret.py
│   └── secret_strength.py
├── test/                    (4 per-test files)
│   ├── is_akeyless_path.py
│   ├── is_akeyless_access_id.py
│   ├── is_pem_block.py
│   └── is_base64.py
├── callback/                (1)
│   └── akeyless_redactor.py
├── action/                  (1, with shadow module)
│   └── secret_to_file.py
├── cache/                   (1)
│   └── akeyless_token.py
└── doc_fragments/           (1, shared auth options)
    └── auth.py
```

## The test pyramid

```
                ┌─────────────────────────────────┐
                │ live-integration                │  431 skipped
                │ (real Akeyless gateway)         │  (env-gated)
                ├─────────────────────────────────┤
                │ tests/mock                      │  269+ wire tests
                │ (mock-server lifecycle)         │
                ├─────────────────────────────────┤
                │ tests/unit                      │  5500+ tests
                │ (per-helper / per-plugin)       │  inc. property
                ├─────────────────────────────────┤
                │ tests/sanity                    │  1500+ tests
                │ (drift prevention)              │
                └─────────────────────────────────┘
```

- **Sanity** layer pins every public surface: CHANGELOG / README /
  plugin DOCUMENTATION YAML / decorator usage per plugin / per-filter
  file structure / lookup helper DRY / filter registration / module
  DOCUMENTATION (per-module) / mutation config / mock-coverage
  breadth / dead-plugin detection / GitHub Actions workflows.
- **Unit** layer covers helpers + plugins with both fixed cases and
  Hypothesis property tests. The redactor + inventory + action
  property tests have already surfaced real fixture bugs that
  fixed-case tests couldn't see.
- **Mock** layer is wire-level — module main() → helper → V2Api
  proxy → SDK method → exit_json. Covers all 4 helper shapes
  (CRUD / action / info / lookup) and the 6 most-used CRUD families
  (role, static_secret, target_*, auth_method_*, dynamic_secret_*,
  rotated_secret_*).
- **Live** runs against a real Akeyless gateway in the
  `integration-live` workflow. Skip-marked under `pytest.skip` when
  the gateway env vars aren't set.

## CI workflows

Nine workflows gate every push:

- `ci.yml` — pytest pyramid sanity (~17s)
- `release.yml` — `ansible-galaxy collection publish` on tag
- `auto-bump.yml` — patch-bump galaxy.yml on every push that
  touches `plugins/` / `meta/` / `galaxy.yml`
- `docs-lint.yml` — antsibull-docs schema check
- `ansible-test.yml` — sanity tests via ansible-test
- `matrix.yml` — multi-Python (3.10 / 3.11 / 3.12 / 3.13)
- `codeql.yml` — security scan
- `integration-live.yml` — real-gateway tests (when secrets set)
- `mutation-test.yml` — nightly mutmut sweep (04:17 UTC)

The release pipeline is autonomous: a code-changing push triggers
auto-bump → tag → release → Galaxy publish in ~4 minutes.

## Test pollution and the conftest fixture

Sequential pytest runs share `sys.modules` across test files. Each
plugin test file installs its own stubs (`ansible.errors`,
`ansible.plugins.lookup`, etc.), and the FIRST install wins. To
prevent contract drift across files, every stub installer is
idempotent and ADDITIVE — they only set an attribute when it isn't
already present.

`tests/unit/conftest.py` also exposes an `install_module_util`
fixture that loads any `plugins/module_utils/<stem>.py` under its
canonical `ansible_collections.drzln0.akeyless.plugins.module_utils.<stem>`
name. New test files can use it instead of repeating the ~15-line
stub installer.

## Generator → collection sync points

When you change the helper architecture in
`plugins/module_utils/akeyless_client.py`:

1. Edit + test here.
2. Sync the SAME change to `ansible-forge/src/client_helper.py`
   (this is what the generator bundles into every regen).
3. Run `nix flake check` here to confirm no regression.
4. The ansible-forge backstop catches drift on every PR via byte-
   exact compare.

Skipping step 2 means the next regen wipes your downstream change.
