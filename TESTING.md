# Testing ReactICS

## Prerequisites

- **BDD module**: compiled (`./reactics setup` or `make` in `reactics-bdd/`)
- **SMT module**: Python 3 with `z3-solver` and `pytest` installed

```
pip install z3-solver pytest
```

## Running all tests

```
bash tests/run_all_tests.sh
```

This runs both the BDD and SMT test suites in sequence.

## BDD tests

```
bash tests/run_tests.sh
```

10 regression tests that run the compiled `reactics-bdd/reactics` binary
against example `.drs` files and compare output to saved baselines in
`tests/expected/`. Covers:

- Parsed system printing (`-P`)
- Reaction listing (`-r`)
- Reachable state enumeration (`-s`)
- RSCTLK model checking (`-c`) for properties f1--f4

Input files: `examples/bdd/tgc.drs`, `examples/bdd/tgc4.drs`,
`reactics-bdd/in/trivial.drs`.

To update baselines after an intentional output change, delete the
relevant file in `tests/expected/` and re-run; the test will regenerate it.

## SMT tests

```
python3 -m pytest tests/test_smt.py -v
```

23 pytest tests exercising the Python API directly. Organised by layer:

- **Data model** -- ReactionSystem, concentrations, context automata,
  formula construction (BagDescription, rsLTL)
- **SmtCheckerRS** -- basic reachability (no concentrations)
- **SmtCheckerRSC** -- reachability and rsLTL model checking with
  concentrations (chain reaction, heat shock response)
- **SmtCheckerRSCParam** -- parametric verification
- **RSC-to-RS translation** -- verifying the translated system
