#!/usr/bin/env bash
# Build a claude.ai upload (zip) for one skill folder.
# state/ (private data) is left out unless --with-state is given; then the link is followed and the current data is bundled.
# Usage: scripts/package_skill.sh [--with-state] <skill-dir> [out-dir]   (default out-dir: dist/)
set -euo pipefail

with_state=0
if [ "${1:-}" = "--with-state" ]; then with_state=1; shift; fi
skill_dir="${1:?usage: scripts/package_skill.sh [--with-state] <skill-dir> [out-dir]}"
out_dir="${2:-dist}"
[ -f "${skill_dir}/SKILL.md" ] || { echo "no SKILL.md in ${skill_dir}" >&2; exit 1; }

name="$(basename "${skill_dir}")"
mkdir -p "${out_dir}"
out="$(cd "${out_dir}" && pwd)/${name}.zip"
rm -f "${out}"

exclude=('*/__pycache__/*' '*.pyc' '*/.DS_Store')
if [ "${with_state}" = 0 ]; then exclude+=("${name}/state" "${name}/state/*"); fi
# zip from the parent so the archive contains <name>/SKILL.md, as claude.ai expects
(cd "$(dirname "${skill_dir}")" && zip -qr "${out}" "${name}" -x "${exclude[@]}")
echo "wrote ${out}"
if [ "${with_state}" = 1 ]; then
  echo "warning: ${out} contains a copy of your private state/ data; upload it only to your own account, never share or commit it" >&2
fi
