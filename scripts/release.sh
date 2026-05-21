#!/usr/bin/env bash
# Copyright: (c) 2026, pleme-io
# MIT License
#
# Build and (optionally) publish an Ansible Galaxy collection tarball.
#
# Usage:
#   VERSION=0.3.0 scripts/release.sh build       # build + validate the tarball
#   VERSION=0.3.0 ANSIBLE_GALAXY_API_KEY=... scripts/release.sh publish
#                                                # build, validate, publish
#
# Side effects:
#   - Temporarily rewrites the `version:` line in galaxy.yml to $VERSION.
#     The original is restored on script exit (trap), so the working copy
#     is not modified beyond the build window.
#   - Produces ./akeyless-akeyless-${VERSION}.tar.gz and a .sha256 sidecar.
#   - In `publish` mode, calls `ansible-galaxy collection publish`.
#
# Required environment:
#   VERSION                 -- semver, e.g. 0.3.0 (must be set; never inferred)
#   ANSIBLE_GALAXY_API_KEY  -- required only in publish mode
#
# Dependencies on PATH:
#   ansible-galaxy (from `ansible-core`), sha256sum, sed, tar
#
# Exit codes:
#   0 success
#   1 usage error
#   2 build failure
#   3 publish failure

set -euo pipefail

# -----------------------------------------------------------------------------
# Argument and environment validation.
# -----------------------------------------------------------------------------

cmd="${1:-build}"
case "${cmd}" in
  build|publish|clean) ;;
  *)
    echo "usage: $0 {build|publish|clean}" >&2
    echo "(env: VERSION=<x.y.z> ANSIBLE_GALAXY_API_KEY=<key>)" >&2
    exit 1
    ;;
esac

if [ "${cmd}" != "clean" ] && [ -z "${VERSION:-}" ]; then
  echo "error: VERSION env var must be set (e.g. VERSION=0.3.0)" >&2
  exit 1
fi

# Resolve repo root from this script's location so the caller can invoke from
# anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

GALAXY_YML="${REPO_ROOT}/galaxy.yml"
NAMESPACE="$(awk '/^namespace:/{print $2; exit}' "${GALAXY_YML}")"
NAME="$(awk '/^name:/{print $2; exit}' "${GALAXY_YML}")"

if [ -z "${NAMESPACE}" ] || [ -z "${NAME}" ]; then
  echo "error: galaxy.yml is missing namespace or name" >&2
  exit 2
fi

# -----------------------------------------------------------------------------
# Subcommands.
# -----------------------------------------------------------------------------

clean_artifacts() {
  rm -f "${REPO_ROOT}/${NAMESPACE}-${NAME}-"*.tar.gz \
        "${REPO_ROOT}/${NAMESPACE}-${NAME}-"*.tar.gz.sha256
}

restore_galaxy_yml() {
  # Best-effort restore from the .bak left by sed -i.bak.
  if [ -f "${GALAXY_YML}.bak" ]; then
    mv "${GALAXY_YML}.bak" "${GALAXY_YML}"
  fi
}

build_tarball() {
  # 1. Stage the version into galaxy.yml. Use sed -i.bak so we have a
  #    portable rollback path on both GNU and BSD sed.
  echo "[release] staging version ${VERSION} into galaxy.yml"
  sed -i.bak "s/^version: .*/version: ${VERSION}/" "${GALAXY_YML}"
  trap restore_galaxy_yml EXIT

  # 2. Build the collection tarball into the repo root. ansible-galaxy
  #    refuses to overwrite, so wipe any prior artifact first.
  clean_artifacts
  echo "[release] running ansible-galaxy collection build"
  ansible-galaxy collection build --output-path "${REPO_ROOT}" --force

  TARBALL="${REPO_ROOT}/${NAMESPACE}-${NAME}-${VERSION}.tar.gz"
  if [ ! -f "${TARBALL}" ]; then
    echo "error: expected ${TARBALL} not found" >&2
    exit 2
  fi

  # 3. Sanity-check the tarball: must install into a scratch path without
  #    error. This catches malformed metadata before the publish call.
  echo "[release] validating tarball install"
  local _scratch
  _scratch="$(mktemp -d)"
  ansible-galaxy collection install \
    --collections-path "${_scratch}" \
    --force \
    "${TARBALL}" >/dev/null

  if [ ! -d "${_scratch}/ansible_collections/${NAMESPACE}/${NAME}" ]; then
    echo "error: tarball installed but layout is wrong" >&2
    exit 2
  fi
  rm -rf "${_scratch}"

  # 4. Compute SHA-256 of the tarball for the GitHub Release asset.
  echo "[release] computing SHA-256"
  sha256sum "${TARBALL}" > "${TARBALL}.sha256"

  echo "[release] OK: ${TARBALL}"
  ls -la "${TARBALL}" "${TARBALL}.sha256"
}

publish_tarball() {
  if [ -z "${ANSIBLE_GALAXY_API_KEY:-}" ]; then
    echo "error: ANSIBLE_GALAXY_API_KEY env var must be set to publish" >&2
    exit 3
  fi

  TARBALL="${REPO_ROOT}/${NAMESPACE}-${NAME}-${VERSION}.tar.gz"
  if [ ! -f "${TARBALL}" ]; then
    echo "[release] tarball not found, building first"
    build_tarball
  fi

  echo "[release] publishing ${TARBALL} to galaxy.ansible.com"
  ansible-galaxy collection publish \
    --api-key "${ANSIBLE_GALAXY_API_KEY}" \
    "${TARBALL}"
  echo "[release] published"
}

case "${cmd}" in
  build)
    build_tarball
    ;;
  publish)
    build_tarball
    publish_tarball
    ;;
  clean)
    clean_artifacts
    restore_galaxy_yml
    echo "[release] cleaned"
    ;;
esac
