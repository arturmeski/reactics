#!/usr/bin/env bash

# Runs all ReactICS regression tests (BDD + SMT + generators)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REACTICS="$ROOT_DIR/reactics-bdd/reactics"
GENERATORS="$ROOT_DIR/examples/bdd/generators"

cd "$ROOT_DIR"

failed=0

# ---------------------------------------------------------------
echo "========== BDD Tests =========="
echo
bash "$SCRIPT_DIR/run_tests.sh" || failed=1

# ---------------------------------------------------------------
echo
echo "========== SMT Tests (pytest) =========="
echo
python3 -m pytest "$SCRIPT_DIR/test_smt.py" -v || failed=1

# ---------------------------------------------------------------
echo
echo "========== Generator Tests =========="
echo

gen_pass=0
gen_fail=0

check_gen() {
    local name="$1"
    local gen_cmd="$2"
    local property="$3"
    local expected="$4"

    local tmpfile
    tmpfile=$(mktemp /tmp/reactics_gen_XXXXXX.drs)

    eval "$gen_cmd" > "$tmpfile" 2>&1
    local result
    result=$("$REACTICS" -c "$property" "$tmpfile" 2>&1 | grep -oE "(holds|does not hold)" || true)
    rm -f "$tmpfile"

    if [[ "$result" == "$expected" ]]; then
        echo "  PASS: $name"
        ((gen_pass++))
    else
        echo "  FAIL: $name (expected '$expected', got '$result')"
        ((gen_fail++))
        failed=1
    fi
}

echo "[gen_tgc]"
check_gen "tgc(3) f1"  "python3 $GENERATORS/gen_tgc.py 3"  f1  "holds"
check_gen "tgc(3) f3"  "python3 $GENERATORS/gen_tgc.py 3"  f3  "holds"
check_gen "tgc(4) f2"  "python3 $GENERATORS/gen_tgc.py 4"  f2  "holds"

echo
echo "[gen_asm]"
check_gen "asm(3) f1"   "python3 $GENERATORS/gen_asm.py 3"   f1  "holds"
check_gen "asm(3) f2"   "python3 $GENERATORS/gen_asm.py 3"   f2  "holds"

echo
echo "[gen_drs]"
check_gen "drs(2,2,2,a) f0"  "python3 $GENERATORS/gen_drs.py 2 2 2 a"  f0  "does not hold"
check_gen "drs(2,2,2,b) f0"  "python3 $GENERATORS/gen_drs.py 2 2 2 b"  f0  "holds"

echo
echo "Generator results: $gen_pass passed, $gen_fail failed"

# ---------------------------------------------------------------
echo
echo "================================"
if [[ $failed -eq 0 ]]; then
    echo "All test suites passed."
else
    echo "Some tests FAILED."
    exit 1
fi
