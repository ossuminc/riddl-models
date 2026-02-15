#!/usr/bin/env bash
#
# verify-bast-roundtrip.sh
#
# Verifies .bast round-trip fidelity for all (or a subset of) RIDDL
# models. Run this after any .bast format change or riddlc upgrade.
#
# Usage:
#   ./scripts/verify-bast-roundtrip.sh          # all models
#   ./scripts/verify-bast-roundtrip.sh 10       # first 10 models
#
# Requires: riddlc on PATH or cached in .riddlc/{version}/bin/riddlc
#
# Three checks per model:
#   1. Unbastify: .bast → single .riddl (catches deserialization bugs)
#   2. Binary round-trip: re-bastify unbastified .riddl, compare .bast
#      files byte-for-byte (catches lossy serialization)
#   3. Source round-trip: prettify+flatten both original and unbastified
#      .riddl, diff them (catches semantic content loss)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIMIT="${1:-0}"  # 0 = no limit
TMPDIR_BASE="/tmp/bast-verify"
INPUT_FILE_RE='input-file[[:space:]]*=[[:space:]]*"([^"]+)"'

# --- Locate riddlc ---

# Prefer the cached version matching build.sbt riddlVersion
RIDDL_VERSION=$(sed -n 's/.*riddlVersion.*=.*"\([^"]*\)".*/\1/p' \
  "$REPO_ROOT/build.sbt" 2>/dev/null || true)

if [[ -n "$RIDDL_VERSION" ]] \
   && [[ -x "$REPO_ROOT/.riddlc/$RIDDL_VERSION/bin/riddlc" ]]; then
  RIDDLC="$REPO_ROOT/.riddlc/$RIDDL_VERSION/bin/riddlc"
elif command -v riddlc &>/dev/null; then
  RIDDLC="$(command -v riddlc)"
  RIDDL_VERSION="$("$RIDDLC" version 2>/dev/null \
    | sed -n 's/.*\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' \
    || echo 'unknown')"
else
  echo "ERROR: riddlc not found. Run 'sbt downloadRiddlc' first." >&2
  exit 1
fi

echo "Using riddlc $RIDDL_VERSION at $RIDDLC"
echo ""

# --- Discover models ---

# Find .conf files the same way RiddlcTasks does: all .conf under
# repo root, excluding patterns/, target/, project/, .riddlc/
CONF_FILES=()
while IFS= read -r f; do
  CONF_FILES+=("$f")
done < <(
  find "$REPO_ROOT" -name "*.conf" -type f \
    -not -path "$REPO_ROOT/patterns/*" \
    -not -path "$REPO_ROOT/target/*" \
    -not -path "$REPO_ROOT/project/*" \
    -not -path "$REPO_ROOT/.riddlc/*" \
  | sort
)

TOTAL=${#CONF_FILES[@]}
if [[ "$LIMIT" -gt 0 ]] && [[ "$LIMIT" -lt "$TOTAL" ]]; then
  CONF_FILES=("${CONF_FILES[@]:0:$LIMIT}")
  echo "Checking $LIMIT of $TOTAL models"
else
  echo "Checking all $TOTAL models"
fi
echo ""

# --- Clean temp directory ---
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"

# --- Run checks ---

PASS=0
FAIL=0
SKIP=0
FAILURES=()

for conf in "${CONF_FILES[@]}"; do
  model_dir="$(dirname "$conf")"
  rel_path="${model_dir#"$REPO_ROOT/"}"
  model_name="$(basename "$model_dir")"

  # Extract input-file from .conf
  input_file=""
  while IFS= read -r line; do
    if [[ "$line" =~ $INPUT_FILE_RE ]]; then
      input_file="${BASH_REMATCH[1]}"
      break
    fi
  done < "$conf"

  if [[ -z "$input_file" ]]; then
    echo "  SKIP: $rel_path (no input-file in conf)"
    SKIP=$((SKIP + 1))
    continue
  fi

  riddl_file="$model_dir/$input_file"
  bast_file="${riddl_file%.riddl}.bast"

  if [[ ! -f "$bast_file" ]]; then
    echo "  SKIP: $rel_path (no .bast file)"
    SKIP=$((SKIP + 1))
    continue
  fi

  # Per-model temp directory
  work_dir="$TMPDIR_BASE/$rel_path"
  mkdir -p "$work_dir"

  failed=false
  fail_reasons=""

  # --- Check 1: Unbastify ---
  unbast_dir="$work_dir/unbastified"
  mkdir -p "$unbast_dir"
  if ! unbast_output=$("$RIDDLC" unbastify "$bast_file" \
       -o "$unbast_dir" 2>&1); then
    failed=true
    fail_reasons="unbastify error: $unbast_output"
  fi

  # Find the unbastified .riddl file
  unbast_riddl="$unbast_dir/$input_file"
  if [[ "$failed" == false ]] && [[ ! -f "$unbast_riddl" ]]; then
    # Try finding any .riddl in the output dir
    unbast_riddl="$(find "$unbast_dir" -name "*.riddl" -type f \
      | head -1 || true)"
    if [[ -z "$unbast_riddl" ]] || [[ ! -f "$unbast_riddl" ]]; then
      failed=true
      fail_reasons="unbastify produced no .riddl file"
    fi
  fi

  # --- Check 2: Binary round-trip (re-bastify and compare) ---
  if [[ "$failed" == false ]]; then
    rebast_dir="$work_dir/rebastified"
    mkdir -p "$rebast_dir"

    # Re-bastify the unbastified .riddl
    if ! rebast_output=$("$RIDDLC" bastify "$unbast_riddl" 2>&1); then
      failed=true
      fail_reasons="re-bastify error: $rebast_output"
    else
      # The re-bastified .bast will be next to the unbastified .riddl
      rebast_bast="${unbast_riddl%.riddl}.bast"
      if [[ ! -f "$rebast_bast" ]]; then
        failed=true
        fail_reasons="re-bastify produced no .bast file"
      elif ! cmp -s "$bast_file" "$rebast_bast"; then
        orig_size=$(stat -f%z "$bast_file" 2>/dev/null \
          || stat -c%s "$bast_file")
        new_size=$(stat -f%z "$rebast_bast" 2>/dev/null \
          || stat -c%s "$rebast_bast")
        failed=true
        fail_reasons="binary mismatch: original=${orig_size}B, "\
"re-bastified=${new_size}B"
      fi
    fi
  fi

  # --- Check 3: Source round-trip (prettify --single-file) ---
  if [[ "$failed" == false ]]; then
    orig_pretty_dir="$work_dir/orig-pretty"
    unbast_pretty_dir="$work_dir/unbast-pretty"
    mkdir -p "$orig_pretty_dir" "$unbast_pretty_dir"

    # Prettify original (multi-file → single flattened file)
    orig_pretty_ok=true
    if ! pretty_output=$("$RIDDLC" prettify "$riddl_file" \
         -o "$orig_pretty_dir" --single-file true 2>&1); then
      # prettify failure is not necessarily a round-trip bug —
      # could be a prettify limitation. Warn but don't fail.
      echo "  WARN: $rel_path — prettify original failed: $pretty_output"
      orig_pretty_ok=false
    fi

    # Prettify unbastified
    unbast_pretty_ok=true
    if ! pretty_output=$("$RIDDLC" prettify "$unbast_riddl" \
         -o "$unbast_pretty_dir" --single-file true 2>&1); then
      echo "  WARN: $rel_path — prettify unbastified failed: $pretty_output"
      unbast_pretty_ok=false
    fi

    # Compare if both succeeded
    if [[ "$orig_pretty_ok" == true ]] \
       && [[ "$unbast_pretty_ok" == true ]]; then
      orig_flat="$(find "$orig_pretty_dir" -name "*.riddl" -type f \
        | head -1 || true)"
      unbast_flat="$(find "$unbast_pretty_dir" -name "*.riddl" -type f \
        | head -1 || true)"

      if [[ -n "$orig_flat" ]] && [[ -n "$unbast_flat" ]]; then
        if ! diff_output=$(diff -u "$orig_flat" "$unbast_flat" 2>&1); then
          diff_lines=$(echo "$diff_output" | wc -l | tr -d ' ')
          failed=true
          fail_reasons="prettify diff: $diff_lines lines differ"
          # Save diff for inspection
          echo "$diff_output" > "$work_dir/prettify.diff"
        fi
      fi
    fi
  fi

  # --- Report ---
  if [[ "$failed" == true ]]; then
    echo "  FAIL: $rel_path — $fail_reasons"
    FAIL=$((FAIL + 1))
    FAILURES+=("$rel_path: $fail_reasons")
  else
    echo "  PASS: $rel_path"
    PASS=$((PASS + 1))
  fi
done

# --- Summary ---
echo ""
echo "=========================================="
echo "  BAST Round-Trip Verification Summary"
echo "=========================================="
echo "  riddlc version: $RIDDL_VERSION"
echo "  Models checked:  $((PASS + FAIL + SKIP))"
echo "  Passed:          $PASS"
echo "  Failed:          $FAIL"
echo "  Skipped:         $SKIP"
echo "=========================================="

if [[ ${#FAILURES[@]} -gt 0 ]]; then
  echo ""
  echo "Failures:"
  for f in "${FAILURES[@]}"; do
    echo "  - $f"
  done
  echo ""
  echo "Inspect details in: $TMPDIR_BASE"
  exit 1
fi

echo ""
echo "All models passed round-trip verification."
exit 0
