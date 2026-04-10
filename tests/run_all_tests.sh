#!/usr/bin/env bash

# Runs all ReactICS regression tests (BDD + SMT)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

failed=0

echo "========== BDD Tests =========="
echo
bash "$SCRIPT_DIR/run_tests.sh" || failed=1

echo
echo "========== SMT Tests (pytest) =========="
echo
python3 -m pytest "$SCRIPT_DIR/test_smt.py" -v || failed=1

echo
if [[ $failed -eq 0 ]]; then
    echo "All test suites passed."
else
    echo "Some tests FAILED."
    exit 1
fi
