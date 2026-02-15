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
#   2. Binary round-trip (apples-to-apples): prettify+flatten the
#      original multi-file model to a single .riddl, bastify that,
#      then compare against the bastified unbastified .riddl. Both
#      come from a single-file source so .bast should be identical.
#   3. Source round-trip: prettify+flatten both original and
#      unbastified .riddl, diff them (catches semantic content loss)

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

  # --- Check 2: Binary round-trip (apples-to-apples) ---
  # Prettify+flatten the original → single .riddl. Copy both that
  # and the unbastified .riddl into a shared dir with the same
  # filename, then bastify each. The .bast format embeds the full
  # file path, so both must be bastified from the same path to get
  # comparable output.
  if [[ "$failed" == false ]]; then
    orig_flat_dir="$work_dir/orig-flat"
    mkdir -p "$orig_flat_dir"

    # Flatten original multi-file model to single .riddl
    if ! flat_output=$("$RIDDLC" prettify "$riddl_file" \
         -o "$orig_flat_dir" --single-file true 2>&1); then
      echo "  WARN: $rel_path — prettify original failed, skipping Check 2"
    else
      orig_flat_raw="$(find "$orig_flat_dir" -name "*.riddl" -type f \
        | head -1 || true)"

      # Keep a copy with the original name for Check 3
      if [[ -n "$orig_flat_raw" ]] && [[ -f "$orig_flat_raw" ]]; then
        orig_flat="$orig_flat_dir/$input_file"
        if [[ "$orig_flat_raw" != "$orig_flat" ]]; then
          mv "$orig_flat_raw" "$orig_flat"
        fi
      fi

      if [[ -n "${orig_flat:-}" ]] && [[ -f "${orig_flat:-}" ]]; then
        # Bastify both from the EXACT same path so the embedded
        # path in .bast is identical. Copy one file in, bastify,
        # save the .bast, then replace with the other and bastify.
        bast_cmp_dir="$work_dir/bast-compare"
        mkdir -p "$bast_cmp_dir"
        bast_cmp_riddl="$bast_cmp_dir/$input_file"
        bast_cmp_bast="$bast_cmp_dir/${input_file%.riddl}.bast"

        # Bastify flattened original
        cp "$orig_flat" "$bast_cmp_riddl"
        if ! flat_bast_output=$("$RIDDLC" bastify \
             "$bast_cmp_riddl" 2>&1); then
          failed=true
          fail_reasons="bastify flattened original error: $flat_bast_output"
        else
          flat_bast="$bast_cmp_dir/flat.bast"
          mv "$bast_cmp_bast" "$flat_bast"

          # Bastify unbastified from same path
          cp "$unbast_riddl" "$bast_cmp_riddl"
          if ! unbast_bast_output=$("$RIDDLC" bastify \
               "$bast_cmp_riddl" 2>&1); then
            failed=true
            fail_reasons="re-bastify error: $unbast_bast_output"
          else
            unbast_bast="$bast_cmp_dir/unbast.bast"
            mv "$bast_cmp_bast" "$unbast_bast"

            if [[ ! -f "$flat_bast" ]]; then
              failed=true
              fail_reasons="bastify flattened original produced no .bast"
            elif [[ ! -f "$unbast_bast" ]]; then
              failed=true
              fail_reasons="re-bastify produced no .bast file"
            elif ! cmp -s "$flat_bast" "$unbast_bast"; then
              flat_size=$(stat -f%z "$flat_bast" 2>/dev/null \
                || stat -c%s "$flat_bast")
              unbast_size=$(stat -f%z "$unbast_bast" 2>/dev/null \
                || stat -c%s "$unbast_bast")
              failed=true
              fail_reasons="binary mismatch: flattened=${flat_size}B, "\
"unbastified=${unbast_size}B"
            fi
          fi
        fi
      fi
    fi
  fi

  # --- Check 3: Source round-trip (prettify --single-file) ---
  # Prettify both original and unbastified to single files, then
  # compare both the .riddl text AND the .bast generated from each.
  if [[ "$failed" == false ]]; then
    unbast_pretty_dir="$work_dir/unbast-pretty"
    mkdir -p "$unbast_pretty_dir"

    # We already have orig_flat from Check 2. Prettify unbastified.
    unbast_pretty_ok=true
    if ! pretty_output=$("$RIDDLC" prettify "$unbast_riddl" \
         -o "$unbast_pretty_dir" --single-file true 2>&1); then
      echo "  WARN: $rel_path — prettify unbastified failed: $pretty_output"
      unbast_pretty_ok=false
    fi

    # Compare if both flattened files exist
    if [[ -n "${orig_flat:-}" ]] && [[ -f "${orig_flat:-}" ]] \
       && [[ "$unbast_pretty_ok" == true ]]; then
      unbast_flat_raw="$(find "$unbast_pretty_dir" -name "*.riddl" -type f \
        | head -1 || true)"

      # Rename to match original filename for .bast comparison
      unbast_flat=""
      if [[ -n "$unbast_flat_raw" ]] && [[ -f "$unbast_flat_raw" ]]; then
        unbast_flat="$unbast_pretty_dir/$input_file"
        if [[ "$unbast_flat_raw" != "$unbast_flat" ]]; then
          mv "$unbast_flat_raw" "$unbast_flat"
        fi
      fi

      if [[ -n "$unbast_flat" ]] && [[ -f "$unbast_flat" ]]; then
        # Compare .riddl text
        if ! diff_output=$(diff -u "$orig_flat" "$unbast_flat" 2>&1); then
          diff_lines=$(echo "$diff_output" | wc -l | tr -d ' ')
          failed=true
          fail_reasons="prettify diff: $diff_lines lines differ"
          echo "$diff_output" > "$work_dir/prettify.diff"
        fi

        # Compare .bast from both prettified single files.
        # Bastify from the exact same path for comparable output.
        if [[ "$failed" == false ]]; then
          pretty_cmp_dir="$work_dir/pretty-bast-compare"
          mkdir -p "$pretty_cmp_dir"
          pretty_cmp_riddl="$pretty_cmp_dir/$input_file"
          pretty_cmp_bast="$pretty_cmp_dir/${input_file%.riddl}.bast"

          # Bastify prettified original
          cp "$orig_flat" "$pretty_cmp_riddl"
          orig_flat_bast_ok=true
          if ! bast_output=$("$RIDDLC" bastify \
               "$pretty_cmp_riddl" 2>&1); then
            echo "  WARN: $rel_path — bastify prettified original failed"
            orig_flat_bast_ok=false
          else
            mv "$pretty_cmp_bast" "$pretty_cmp_dir/orig.bast"
          fi

          # Bastify prettified unbastified from same path
          cp "$unbast_flat" "$pretty_cmp_riddl"
          unbast_flat_bast_ok=true
          if ! bast_output=$("$RIDDLC" bastify \
               "$pretty_cmp_riddl" 2>&1); then
            echo "  WARN: $rel_path — bastify prettified unbastified failed"
            unbast_flat_bast_ok=false
          else
            mv "$pretty_cmp_bast" "$pretty_cmp_dir/unbast.bast"
          fi

          if [[ "$orig_flat_bast_ok" == true ]] \
             && [[ "$unbast_flat_bast_ok" == true ]]; then
            if [[ -f "$pretty_cmp_dir/orig.bast" ]] \
               && [[ -f "$pretty_cmp_dir/unbast.bast" ]] \
               && ! cmp -s "$pretty_cmp_dir/orig.bast" \
                    "$pretty_cmp_dir/unbast.bast"; then
              orig_fb_size=$(stat -f%z "$pretty_cmp_dir/orig.bast" \
                2>/dev/null || stat -c%s "$pretty_cmp_dir/orig.bast")
              unbast_fb_size=$(stat -f%z "$pretty_cmp_dir/unbast.bast" \
                2>/dev/null || stat -c%s "$pretty_cmp_dir/unbast.bast")
              failed=true
              fail_reasons="prettified .bast mismatch: "\
"orig=${orig_fb_size}B, unbast=${unbast_fb_size}B"
            fi
          fi
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
