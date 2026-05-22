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

        # Shared bootstrap for any app that needs the live-test Python
        # environment (ansible + akeyless SDK + pytest + xdist + timeout).
        # The single source of truth is the repo's pyproject.toml +
        # uv.lock; we materialize a hermetic venv via `uv sync --frozen`,
        # pinning the interpreter to nix's python3 so the resulting
        # tree is fully reproducible. Cached under XDG_CACHE_HOME so
        # repeat runs of the same lockfile are near-instant.
        #
        # Sets PATH so subsequent commands resolve pytest/ansible/etc.
        # from the venv. Idempotent: re-running with an unchanged
        # uv.lock is a noop.
        uvSyncSnippet = ''
          cache="''${XDG_CACHE_HOME:-$HOME/.cache}/ansible-akeyless-livetest"
          lockhash=$(${pkgs.coreutils}/bin/sha256sum uv.lock | ${pkgs.coreutils}/bin/cut -d' ' -f1)
          if [ ! -f "$cache/.lockhash" ] || [ "$(cat "$cache/.lockhash")" != "$lockhash" ]; then
            echo "[uv-sync] materializing venv for uv.lock $lockhash"
            ${pkgs.uv}/bin/uv sync --frozen --python ${pkgs.python3}/bin/python3 \
              --project "$PWD" --no-progress 2>&1 | ${pkgs.gnugrep}/bin/grep -vE '^(Using|Resolved|Installed|Audited|Built|\s+\+)' || true
            mkdir -p "$cache"
            echo "$lockhash" > "$cache/.lockhash"
          fi
          export PATH="$PWD/.venv/bin:$PATH"
        '';

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
            # Per-module live coverage matrix. Runs every plugins/modules/*.py
            # against real Akeyless with auto-derived minimal args, classifies
            # each outcome (WORKS / ARGSPEC_DRIFT / NEEDS_PREREQ / DISPATCH_FAIL),
            # writes a matrix to tests/live/MATRIX.json. Only DISPATCH_FAIL
            # (real Python-side bug) fails the suite.
            live-coverage = {
              type = "app";
              program = toString (pkgs.writeShellScript "drzln0-akeyless-live-coverage" ''
                set -euo pipefail
                : "''${NIX_REPO_PATH:=$PWD/../nix}"
                secrets_yaml="$NIX_REPO_PATH/secrets.yaml"
                ${uvSyncSnippet}
                dec="$(mktemp)"
                trap 'shred -u "$dec" 2>/dev/null || rm -f "$dec"' EXIT
                ${pkgs.sops}/bin/sops --decrypt "$secrets_yaml" > "$dec"
                chmod 600 "$dec"
                export AKEYLESS_ACCESS_ID="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-id"]'  "$dec")"
                export AKEYLESS_ACCESS_KEY="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-key"]' "$dec")"
                export AKEYLESS_GATEWAY_URL="''${AKEYLESS_GATEWAY_URL:-https://api.akeyless.io}"
                pytest tests/live/coverage_matrix.py -q --tb=no -p no:cacheprovider \
                  -n ''${PYTEST_WORKERS:-8} --timeout=''${PYTEST_TIMEOUT:-60} 2>&1 | tail -10
                echo ""
                echo "=== coverage matrix summary ==="
                python3 - <<'PY'
                import json, pathlib, collections
                m = json.loads(pathlib.Path("tests/live/MATRIX.json").read_text())
                counts = collections.Counter(v["category"] for v in m.values())
                print(f"total modules: {len(m)}")
                for cat, n in counts.most_common():
                    print(f"  {cat:20s} {n:4d}")
                PY
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

                podman="${pkgs.podman}/bin/podman"
                : "''${NIX_REPO_PATH:=$PWD/../nix}"
                secrets_yaml="$NIX_REPO_PATH/secrets.yaml"
                container_name="akeyless-gw-coverage"
                cluster_name="cov-$(date +%s)"

                # vfs storage so rootless podman can unpack the akeyless
                # image. (overlay fails because the image chowns to UID
                # 89939 which exceeds the default subuid mapping.)
                mkdir -p "$HOME/.config/containers"
                if [ ! -f "$HOME/.config/containers/storage.conf" ]; then
                  cat > "$HOME/.config/containers/storage.conf" <<EOF
                [storage]
                driver = "vfs"
                runroot = "/run/user/$(id -u)/containers"
                graphroot = "$HOME/.local/share/containers/storage"
                [storage.options]
                ignore_chown_errors = "true"
                EOF
                fi

                # Decrypt creds to tmpfile, shred on exit + always remove container.
                dec="$(mktemp)"
                cleanup() {
                  shred -u "$dec" 2>/dev/null || rm -f "$dec"
                  "$podman" stop "$container_name" >/dev/null 2>&1 || true
                  "$podman" rm "$container_name" >/dev/null 2>&1 || true
                }
                trap cleanup EXIT
                ${pkgs.sops}/bin/sops --decrypt "$secrets_yaml" > "$dec"
                chmod 600 "$dec"
                access_id="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-id"]'  "$dec")"
                access_key="$(${pkgs.yq-go}/bin/yq -r '.akeyless["access-key"]' "$dec")"

                # Remove stale container from prior run.
                "$podman" rm -f "$container_name" >/dev/null 2>&1 || true

                echo "[gateway] pulling akeyless/base (first run ~2min)…"
                "$podman" pull -q docker.io/akeyless/base:latest

                echo "[gateway] starting $container_name (cluster $cluster_name)…"
                "$podman" run -d --name "$container_name" \
                  -e ADMIN_ACCESS_ID="$access_id" \
                  -e ADMIN_ACCESS_KEY="$access_key" \
                  -e CLUSTER_NAME="$cluster_name" \
                  -p 8000:8000 -p 8080:8080 -p 8081:8081 \
                  -p 8200:8200 -p 18888:18888 \
                  docker.io/akeyless/base:latest >/dev/null

                # Wait for the SDK port (8081) to start serving /auth.
                # Bootstrap takes ~45s on first run.
                echo -n "[gateway] waiting for /auth…"
                for i in $(seq 1 120); do
                  body="$(${pkgs.curl}/bin/curl -sS --max-time 3 -X POST \
                    http://localhost:8081/auth -H 'Content-Type: application/json' \
                    -d "{\"access-id\":\"$access_id\",\"access-key\":\"$access_key\",\"access-type\":\"access_key\"}" || true)"
                  if echo "$body" | grep -q '"token"'; then
                    echo " ready ($i s)"
                    break
                  fi
                  echo -n .; sleep 1
                  if [ "$i" -eq 120 ]; then
                    echo " TIMEOUT after 120s"
                    "$podman" logs --tail=30 "$container_name" >&2
                    exit 1
                  fi
                done

                # /auth responding doesn't mean the gateway has finished
                # warming up its sub-services (KMIP, dynamic-secret
                # validator, etc.). A short warmup avoids the burst of
                # ConnectionReset errors we get from racing the first
                # worker against the gateway's still-initializing back end.
                echo "[gateway] warming up (10s)…"
                sleep 10

                ${uvSyncSnippet}
                export AKEYLESS_ACCESS_ID="$access_id"
                export AKEYLESS_ACCESS_KEY="$access_key"
                export AKEYLESS_GATEWAY_URL="http://localhost:8081"
                # 15s per call: gateway-bound ops dial real services to
                # validate stub data; without this, the matrix takes
                # 60+ min instead of ~5.
                export AKEYLESS_REQUEST_TIMEOUT="''${AKEYLESS_REQUEST_TIMEOUT:-15}"

                # Default to 1 worker for the gateway path -- the gateway
                # serializes most of its expensive ops anyway (dial-out
                # validation for dynamic-secret-create, KMIP cluster
                # boot, etc.) and high xdist concurrency just causes
                # ConnectionReset cascades against a freshly-booted
                # gateway. Override via PYTEST_WORKERS=4 once you're
                # confident your gateway+account can handle it.
                pytest tests/live/coverage_matrix.py -q --tb=line -p no:cacheprovider \
                  -n ''${PYTEST_WORKERS:-1} --timeout=''${PYTEST_TIMEOUT:-90} 2>&1 | tail -10
                echo ""
                echo "=== coverage matrix summary (LOCAL GATEWAY) ==="
                python3 - <<'PY'
                import json, pathlib, collections
                m = json.loads(pathlib.Path("tests/live/MATRIX.json").read_text())
                counts = collections.Counter(v["category"] for v in m.values())
                print(f"total modules: {len(m)}")
                for cat, n in counts.most_common():
                    print(f"  {cat:20s} {n:4d}")
                PY
              '');
            };

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

                ${uvSyncSnippet}

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
                ansible-galaxy collection build --force --output-path .build
                tarball=$(ls -1 .build/*.tar.gz | head -n1)
                ansible-galaxy collection install "$tarball" --force

                # Run every live example. Any failure fails the app.
                shopt -s nullglob
                plays=(examples/live/*.yml examples/live/*.yaml)
                if [ ''${#plays[@]} -eq 0 ]; then
                  echo "no live example playbooks under examples/live/"; exit 0
                fi
                failures=0
                for p in "''${plays[@]}"; do
                  echo "::group::ansible-playbook $p"
                  if ansible-playbook "$p"; then
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
