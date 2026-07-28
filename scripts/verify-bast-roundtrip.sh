#!/usr/bin/env bash
#
# verify-bast-roundtrip.sh
#
# Verifies that every model survives a BAST round trip without discrepancy.
# Run after any .bast format change or riddlc upgrade.
#
# Usage:
#   ./scripts/verify-bast-roundtrip.sh          # all models
#   ./scripts/verify-bast-roundtrip.sh 10       # first 10 models
#
# Per model:
#   1. bastify   <model>.riddl        -> <model>.bast  (written beside the source)
#   2. unbastify <model>.bast -o TMP  -> .riddl files regenerated from the BAST
#   3. diff the regenerated tree against the canonical source, byte for byte
#
# Step 3 is only meaningful because the corpus is kept in `riddlc prettify`
# canonical form, and unbastify emits that same form. Any textual difference is
# therefore a real round-trip discrepancy, not a formatting artefact. Keeping
# the corpus canonical is what makes this an exact comparison instead of a
# fuzzy one -- do not "fix" a failure here by relaxing the diff.
#
# Requires: ../bin/riddlc (override with RIDDLC=...)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
RIDDLC=${RIDDLC:-$(cd "$ROOT/.." && pwd)/bin/riddlc}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$ROOT" || exit 1

if [ ! -x "$RIDDLC" ]; then
  echo "riddlc not found at $RIDDLC (set RIDDLC=/path/to/riddlc)" >&2
  exit 2
fi

DIRS=($(find . -name "*.conf" -not -path "./patterns/*" -exec dirname {} \; \
        | sed 's|^\./||' | sort -u))
[ $# -gt 0 ] && DIRS=("${DIRS[@]:0:$1}")

pass=0; fail=0; failed=()
for d in "${DIRS[@]}"; do
  name=$(basename "$d")
  src="$ROOT/$d"
  bast="$src/$name.bast"

  if ! ( cd "$src" && "$RIDDLC" bastify "$name.riddl" ) >/dev/null 2>&1 || [ ! -f "$bast" ]; then
    echo "FAIL  $d  (bastify produced no .bast)"; failed+=("$d"); fail=$((fail+1)); continue
  fi

  out="$TMP/$(echo "$d" | tr '/' '_')"
  if ! "$RIDDLC" unbastify "$bast" -o "$out" >/dev/null 2>&1; then
    echo "FAIL  $d  (unbastify failed)"; failed+=("$d"); fail=$((fail+1)); continue
  fi

  bad=0
  while IFS= read -r rel; do
    a="$src/$rel"; b="$out/$rel"
    if [ ! -f "$b" ]; then
      echo "FAIL  $d/$rel  (missing after round trip)"; bad=1; continue
    fi
    if ! cmp -s "$a" "$b"; then
      echo "FAIL  $d/$rel  (differs)"
      diff "$a" "$b" | head -6 | sed 's/^/        /'
      bad=1
    fi
  done < <(cd "$src" && find . -name "*.riddl" | sed 's|^\./||')

  if [ "$bad" -eq 0 ]; then pass=$((pass+1)); else failed+=("$d"); fail=$((fail+1)); fi
done

echo
echo "models passing round trip : $pass"
echo "models with discrepancies : $fail"
if [ "$fail" -gt 0 ]; then
  printf '  %s\n' "${failed[@]}"
  exit 1
fi
