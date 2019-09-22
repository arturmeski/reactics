# ReactICS

Reaction Systems Verification Toolkit

The toolkit consists of two separate modules implementing:
* BDD-based methods
* SMT-based methods

## Example

The `examples` directory contains sample input files.

To quickly the BDD module you can perform verification of the TGC controller consiting of three trains:

```
$ ./reactics bdd -c f1 examples/bdd/tgc.rs
```

The above command tests the formula labelled `f1` in the input file.

To test the SMT module you can perform reachability verification of the scalable chain system:

```
$ ./reactics smt examples/smt/chain_reaction.py 2 3 1
```

