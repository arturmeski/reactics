#!/usr/bin/env bash

# Regression test harness for ReactICS BDD module
# Compares current output against saved expected output

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REACTICS="$ROOT_DIR/reactics-bdd/reactics"
EXPECTED_DIR="$SCRIPT_DIR/expected"

PASS=0
FAIL=0
ERRORS=""

run_test() {
    local name="$1"
    local expected_file="$2"
    shift 2
    local actual
    actual=$("$@" 2>&1) || true
    local expected
    expected=$(cat "$expected_file")

    if [[ "$actual" == "$expected" ]]; then
        echo "  PASS: $name"
        ((PASS++))
    else
        echo "  FAIL: $name"
        diff <(echo "$expected") <(echo "$actual") | head -20
        ((FAIL++))
        ERRORS="$ERRORS\n  - $name"
    fi
}

echo "Running ReactICS regression tests..."
echo

# --- tgc.drs tests ---
echo "[tgc]"
run_test "tgc print"      "$EXPECTED_DIR/tgc_print.txt"      "$REACTICS" -P examples/bdd/tgc.drs
run_test "tgc reactions"   "$EXPECTED_DIR/tgc_reactions.txt"   "$REACTICS" -r examples/bdd/tgc.drs
run_test "tgc states"      "$EXPECTED_DIR/tgc_states.txt"      "$REACTICS" -s examples/bdd/tgc.drs
run_test "tgc mc (f1-f4)"  "$EXPECTED_DIR/tgc_mc.txt" \
    bash -c 'for f in f1 f2 f3 f4; do '"$REACTICS"' -c $f examples/bdd/tgc.drs 2>&1; done'

echo
echo "[trivial]"
run_test "trivial print"      "$EXPECTED_DIR/trivial_print.txt"      "$REACTICS" -P reactics-bdd/in/trivial.drs
run_test "trivial reactions"  "$EXPECTED_DIR/trivial_reactions.txt"   "$REACTICS" -r reactics-bdd/in/trivial.drs
run_test "trivial states"     "$EXPECTED_DIR/trivial_states.txt"      "$REACTICS" -s reactics-bdd/in/trivial.drs

echo
echo "[tgc4]"
run_test "tgc4 print"      "$EXPECTED_DIR/tgc4_print.txt"      "$REACTICS" -P examples/bdd/tgc4.drs
run_test "tgc4 states"     "$EXPECTED_DIR/tgc4_states.txt"      "$REACTICS" -s examples/bdd/tgc4.drs
run_test "tgc4 mc (f1-f4)" "$EXPECTED_DIR/tgc4_mc.txt" \
    bash -c 'for f in f1 f2 f3 f4; do '"$REACTICS"' -c $f examples/bdd/tgc4.drs 2>&1; done'

echo
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
    echo -e "Failures:$ERRORS"
    exit 1
else
    echo "All tests passed."
fi
