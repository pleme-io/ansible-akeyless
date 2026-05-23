{
  description = "drzln0.akeyless — auto-generated Ansible collection for Akeyless Vault";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
    substrate.url = "github:pleme-io/substrate";
    substrate.inputs.nixpkgs.follows = "nixpkgs";
    # tatara-lisp ships the `tatara-script` binary that every substrate
    # ansible-collection app is now written against. We pin it explicitly
    # so CI runners + local dev resolve identically (substrate's helper
    # accepts an opt-in `tataraScript` derivation; without it, the
    # wrapper assumes the binary is on PATH).
    tatara-lisp.url = "github:pleme-io/tatara-lisp";
    tatara-lisp.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, substrate, tatara-lisp, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        ansibleCollection = import "${substrate}/lib/infra/ansible-collection.nix";

        # Wrapper that turns a .tlisp file into something `nix run` can
        # invoke. The actual logic of each flake app lives in
        # tests/live/scripts/*.tlisp (read-file-from-disk -> compiled by
        # tatara-script). The only shell remaining in the apps is the
        # uvSyncSnippet that materializes the venv path into PATH; the
        # rest -- sops decrypt, podman lifecycle, pytest invocation,
        # matrix summary -- runs in typed tatara-lisp.
        mkTataraScript = import "${substrate}/lib/scripting/mkTataraScript.nix" {
          inherit pkgs;
          tataraScript = tatara-lisp.packages.${system}.tatara-script;
        };
        base = ansibleCollection.mkAnsibleCollection pkgs {
          namespace = "drzln0";
          name = "akeyless";
          # version source of truth = galaxy.yml; bumped via `nix run .#bump`.
          version = "0.1.0";
          src = self;
          description = "Auto-generated Ansible collection wrapping the Akeyless V2 API.";
          authors = [ "pleme-io" ];
          license = [ "MIT" ];
          minAnsibleVersion = "2.14.0";
          tataraScript = tatara-lisp.packages.${system}.tatara-script;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pytest pyyaml jsonschema hypothesis
        ]);

        # Shared bootstrap for any flake app whose body wants to invoke
        # uv-locked Python tools (pytest/ansible/akeyless SDK). The
        # single source of truth is the repo's pyproject.toml + uv.lock;
        # the snippet materializes a hermetic .venv via `uv sync
        # --frozen`, pins nix python3, caches by lockhash so re-runs
        # are noops, and exports `.venv/bin` to PATH.
        #
        # Pulled from substrate so any other ansible-collection (or
        # python-test) repo gets the exact same behavior just by
        # importing substrateLib.mkUvSyncSnippet.
        uvSyncSnippet = (import "${substrate}/lib/build/python/uv-test-runner.nix").mkUvSyncSnippet {
          inherit pkgs;
          cacheSubdir = "ansible-akeyless-livetest";
        };

        # Three flake checks express the test pyramid as Nix derivations so
        # `nix flake check` runs everything reproducibly — no shell glue in
        # the repo, and CI invokes one command.
        smokeCheck = pkgs.runCommand "smoke" {
          nativeBuildInputs = [ pythonEnv ];
          src = self;
        } ''
          cp -r $src ./work && cd work && chmod -R +w .
          python3 tests/sanity/smoke.py
          touch $out
        '';

        unitCheck = pkgs.runCommand "unit-tests" {
          nativeBuildInputs = [ pythonEnv pkgs.ansible ];
          src = self;
        } ''
          cp -r $src ./work && cd work && chmod -R +w .
          python3 -m pytest tests/unit/ -q
          touch $out
        '';

        # Mock-driven SDK tests -- spin up a fake akeyless package via
        # conftest and drive each module's main() against it. These were
        # historically run locally only; promoting them to a flake check
        # means every PR has to pass them before merge.
        mockCheck = pkgs.runCommand "mock-tests" {
          nativeBuildInputs = [ pythonEnv pkgs.ansible ];
          src = self;
        } ''
          cp -r $src ./work && cd work && chmod -R +w .
          python3 -m pytest tests/mock/ -q
          touch $out
        '';

        # Sanity tests -- collection-level metadata invariants (galaxy.yml,
        # meta/runtime.yml, doc_fragments/auth.py) + the smoke test wrapped
        # as pytest. Cheap (<1s) but catches release-blocking misedits to
        # the manifest before substrate-bump fires.
        sanityCheck = pkgs.runCommand "sanity-tests" {
          nativeBuildInputs = [ pythonEnv ];
          src = self;
        } ''
          cp -r $src ./work && cd work && chmod -R +w .
          python3 -m pytest tests/sanity/ -q --ignore=tests/sanity/smoke.py
          touch $out
        '';

        openapiCheck = pkgs.runCommand "openapi-coverage" {
          nativeBuildInputs = [ pythonEnv ];
          src = self;
          # CI sets AKEYLESS_OPENAPI_YAML to the freshly-fetched spec; this
          # local path lets `nix flake check` work in a dev checkout.
          AKEYLESS_OPENAPI_YAML = "/home/drzzln/code/github/pleme-io/akeyless-go/api/openapi.yaml";
        } ''
          cp -r $src ./work && cd work && chmod -R +w .
          python3 -m pytest tests/openapi/ -q
          touch $out
        '';
      in
        base // {
          checks = {
            smoke = smokeCheck;
            unit = unitCheck;
            mock = mockCheck;
            sanity = sanityCheck;
            openapi = openapiCheck;
          };

          # Umbrella release app: run all checks, build, then publish iff
          # the Galaxy token is in env. CI calls this single entry point.
          apps = base.apps // {
            release = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-release" ''
                set -euo pipefail
                ${pkgs.nix}/bin/nix flake check --no-warn-dirty
                ${pkgs.nix}/bin/nix run .#build
                if [ -n "''${ANSIBLE_GALAXY_TOKEN:-}" ]; then
                  ${pkgs.nix}/bin/nix run .#publish
                else
                  echo "[release] ANSIBLE_GALAXY_TOKEN not set — skipping publish (tarball is built)"
                fi
              '');
            };

            # Local-only live-test: decrypts pleme-io/nix's SOPS-managed
            # akeyless dev creds, exports as env, runs examples/live/*.yml
            # against the real Akeyless cloud API.
            #
            # This is what we run BEFORE every release to know the modules
            # work end-to-end. Open-source CI runs only the cred-free
            # tests (mock --check, openapi coverage); this app is the
            # local attestation that the things requiring auth also pass.
            #
            # Requires:
            #   - sops + age installed (default in our dev shell)
            #   - age key at ~/.config/sops/age/keys.txt (or SOPS_AGE_KEY_FILE)
            #   - pleme-io/nix cloned at ../nix (or NIX_REPO_PATH set)
            #
            # Usage:
            #   nix run .#live-test
            # Per-module live coverage matrix. Runs every plugins/modules/*.py
            # against real Akeyless with auto-derived minimal args, classifies
            # each outcome (WORKS / ARGSPEC_DRIFT / NEEDS_PREREQ / DISPATCH_FAIL),
            # writes a matrix to tests/live/MATRIX.json. Only DISPATCH_FAIL
            # (real Python-side bug) fails the suite.
            # The wrapper shell does the bare minimum: tell uv-sync where
            # to materialize the venv (so PATH points at the lock-pinned
            # pytest/ansible), then hand off to the typed tatara-lisp
            # script. All logic -- sops decrypt, env plumbing, pytest
            # invocation, matrix summary -- runs in .tlisp.
            live-coverage = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-live-coverage" ''
                set -euo pipefail
                : "''${PWD:=$(pwd)}"
                ${uvSyncSnippet}
                exec ${mkTataraScript "live-coverage" (builtins.readFile ./tests/live/scripts/live-coverage.tlisp)}
              '');
            };

            # Spins up an Akeyless Gateway (akeyless/base) in a local
            # rootless podman container, registers it against the dev
            # account from secrets.yaml, then runs the coverage matrix
            # against http://localhost:8081 (SDK path). The gateway
            # unlocks the ~90 "command is not available on public
            # gateway" modules so their dispatch + SDK-shape can be
            # validated end-to-end. Container is torn down on exit.
            #
            # Storage uses vfs + ignore_chown_errors because rootless
            # podman with the default subuid range (65536) can't unpack
            # the akeyless image's UID 89939 files under overlay.
            live-coverage-gateway = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-live-coverage-gateway" ''
                set -euo pipefail
                : "''${PWD:=$(pwd)}"
                # vfs storage so rootless podman can unpack the akeyless
                # image. (overlay fails because the image chowns to UID
                # 89939 which exceeds the default subuid mapping.) This
                # is a one-shot config write -- safely re-runnable.
                ${pkgs.coreutils}/bin/mkdir -p "$HOME/.config/containers"
                if [ ! -f "$HOME/.config/containers/storage.conf" ]; then
                  ${pkgs.coreutils}/bin/cat > "$HOME/.config/containers/storage.conf" <<EOF
                [storage]
                driver = "vfs"
                runroot = "/run/user/$(${pkgs.coreutils}/bin/id -u)/containers"
                graphroot = "$HOME/.local/share/containers/storage"
                [storage.options]
                ignore_chown_errors = "true"
                EOF
                fi
                ${uvSyncSnippet}
                # The tlisp script needs absolute paths for the external
                # tools it shells out to (podman, curl). Resolving them
                # at Nix-eval time means we never PATH-shop at runtime.
                export PODMAN_BIN=${pkgs.podman}/bin/podman
                export CURL_BIN=${pkgs.curl}/bin/curl
                exec ${mkTataraScript "live-coverage-gateway" (builtins.readFile ./tests/live/scripts/live-coverage-gateway.tlisp)}
              '');
            };

            live-test = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-live-test" ''
                set -euo pipefail
                : "''${PWD:=$(pwd)}"
                ${uvSyncSnippet}
                exec ${mkTataraScript "live-test" (builtins.readFile ./tests/live/scripts/live-test.tlisp)}
              '');
            };
          };
        }
    );
}
