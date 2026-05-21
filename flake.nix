{
  description = "drzln0.akeyless — auto-generated Ansible collection for Akeyless Vault";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
    substrate.url = "github:pleme-io/substrate";
    substrate.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, substrate, ... }:
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
          };
        }
    );
}
