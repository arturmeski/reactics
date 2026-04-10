#!/usr/bin/env bash
# Run all ReactICS tests (BDD, SMT, generators)
exec bash "$(dirname "$0")/tests/run_all_tests.sh" "$@"
