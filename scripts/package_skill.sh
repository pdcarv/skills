#!/usr/bin/env bash
# Build a claude.ai upload (zip) for one skill folder.
# Symlinks are followed, so a state/ link is bundled as a copy of the current data.
# Usage: scripts/package_skill.sh <skill-dir> [out-dir]   (default out-dir: dist/)
set -euo pipefail

skill_dir="${1:?usage: scripts/package_skill.sh <skill-dir> [out-dir]}"
out_dir="${2:-dist}"
[ -f "${skill_dir}/SKILL.md" ] || { echo "no SKILL.md in ${skill_dir}" >&2; exit 1; }

name="$(basename "${skill_dir}")"
mkdir -p "${out_dir}"
out="$(cd "${out_dir}" && pwd)/${name}.zip"
rm -f "${out}"

# zip from the parent so the archive contains <name>/SKILL.md, as claude.ai expects
(cd "$(dirname "${skill_dir}")" && zip -qr "${out}" "${name}" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store')
echo "wrote ${out}"
