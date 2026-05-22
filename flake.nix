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
          pytest pyyaml jsonschema
        ]);

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
            live-test = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-live-test" ''
                set -euo pipefail

                : "''${NIX_REPO_PATH:=$PWD/../nix}"
                secrets_yaml="$NIX_REPO_PATH/secrets.yaml"
                if [ ! -f "$secrets_yaml" ]; then
                  echo "::error::secrets.yaml not found at $secrets_yaml (set NIX_REPO_PATH)" >&2
                  exit 1
                fi

                # Decrypt to a tmpfile, extract, then shred. The decrypted
                # plaintext never crosses a logged boundary.
                dec="$(mktemp)"
                trap 'shred -u "$dec" 2>/dev/null || rm -f "$dec"' EXIT
                ${pkgs.sops}/bin/sops --decrypt "$secrets_yaml" > "$dec"
                chmod 600 "$dec"

                AKEYLESS_ACCESS_ID="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-id"]'  "$dec")"
                AKEYLESS_ACCESS_KEY="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-key"]' "$dec")"
                export AKEYLESS_ACCESS_ID AKEYLESS_ACCESS_KEY
                export AKEYLESS_GATEWAY_URL="''${AKEYLESS_GATEWAY_URL:-https://api.akeyless.io}"

                # Build + install the collection so playbooks resolve modules.
                ${pkgs.nix}/bin/nix run .#build
                tarball=$(ls -1 ./*.tar.gz | head -n1)
                ${pkgs.ansible}/bin/ansible-galaxy collection install "$tarball" --force

                # Run every live example. Any failure fails the app.
                shopt -s nullglob
                plays=(examples/live/*.yml examples/live/*.yaml)
                if [ ''${#plays[@]} -eq 0 ]; then
                  echo "no live example playbooks under examples/live/"; exit 0
                fi
                failures=0
                for p in "''${plays[@]}"; do
                  echo "::group::ansible-playbook $p"
                  if ${pkgs.ansible}/bin/ansible-playbook "$p"; then
                    echo "ok: $p"
                  else
                    failures=$((failures + 1))
                    echo "::error file=$p::live ansible-playbook failed"
                  fi
                  echo "::endgroup::"
                done
                if [ "$failures" -gt 0 ]; then
                  echo "::error::$failures live example(s) failed"
                  exit 1
                fi
                echo "all ''${#plays[@]} live example(s) passed against real Akeyless"
              '');
            };
          };
        }
    );
}
