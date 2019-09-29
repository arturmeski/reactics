# ReactICS

Reaction Systems Verification Toolkit

The toolkit consists of two separate modules implementing:
* Methods implemented using binary decision diagrams (BDD) for storing and manipulating the state space of the verified system.
* Methods translating the verification problems into satisfiability modulo theories (SMT).

## Examples

The `examples` directory contains sample input files.

To quickly test the BDD module you can perform verification of the TGC controller consiting of three trains:

```
$ ./reactics bdd -c f1 examples/bdd/tgc.rs
```

The above command tests the formula labelled `f1` in the input file.

To test the SMT module you can perform reachability verification of the scalable chain system:

```
$ ./reactics smt examples/smt/chain_reaction.py 2 3 1
```

### Reaction synthesis

To test the reaction synthesis approach on a mutual exclution protocol modelling three processes, run the following command:

```
./reactics smt examples/smt/mutex_param.py -n 3 -s 1 -o
```


