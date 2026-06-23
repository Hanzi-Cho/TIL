#!/usr/bin/env bash

set -euo pipefail

TARGET_DIR="${1:-src/design-system/components}"

echo "Checking components under: ${TARGET_DIR}"

find "${TARGET_DIR}" -type f \( -name "*.tsx" -o -name "*.ts" \) | while read -r file; do
  echo
  echo "[FILE] ${file}"

  if grep -q "className" "${file}"; then
    echo "  - className prop: ok"
  else
    echo "  - className prop: missing"
  fi

  if grep -q "aria-" "${file}"; then
    echo "  - accessibility attr: found"
  else
    echo "  - accessibility attr: review needed"
  fi

  if grep -q "var(--" "${file}"; then
    echo "  - token usage: found"
  else
    echo "  - token usage: review needed"
  fi
done
