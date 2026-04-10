#!/usr/bin/env python3
"""
Generator for the Mutual Exclusion (Mutex) benchmark.

Produces a reaction system modelling N processes competing for
exclusive access to a critical section, using activation signals,
request tokens, and a lock. Generates one of three RSCTL properties.

NOTE: generates old-syntax input (context-entities, initial-contexts,
rsctl-property) which is not compatible with the current parser.
"""

import argparse


def generate(n, formula):
    out = "reactions {\n"
    for i in range(n):
        out += "\t{{{{out{i},act{i}}},{{}} -> {{request{i}}}}};\n".format(i=i)
        out += "\t{{{{out{i}}},{{act{i}}} -> {{out{i}}}}};\n".format(i=i)

        for j in range(n):
            if i != j:
                out += "\t{{{{request{i},act{i},act{j}}},{{}} -> {{request{i}}}}};\n".format(
                    i=i, j=j)

        out += "\t{{{{request{i}}},{{act{i}}} -> {{request{i}}}}};\n".format(i=i)

        other_acts = ",".join("act" + str(j) for j in range(n) if i != j)
        out += "\t{{{{request{i},act{i}}},{{{others},lock}} -> {{in{i},lock}}}};\n".format(
            i=i, others=other_acts)

        out += "\t{{{{in{i},act{i}}},{{}} -> {{out{i},done}}}};\n".format(i=i)
        out += "\t{{{{in{i}}},{{act{i}}} -> {{in{i}}}}};\n".format(i=i)

    out += "\t{{lock},{done} -> {lock}};\n"
    out += "}\n"

    ctx_ents = ",".join("act" + str(i) for i in range(n))
    out += "context-entities {{ {} }}\n".format(ctx_ents)

    init_ents = ",".join("out" + str(i) for i in range(n))
    out += "initial-contexts {{ {{{}}} }}\n".format(init_ents)

    if formula == 1:
        out += "rsctl-property { A[{act1}]F(in1) }\n"
    elif formula == 2:
        out += "rsctl-property { E[{act1}]F(in1) }\n"
    elif formula == 3:
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append("~(in{} AND in{})".format(i, j))
        out += "rsctl-property {{ AG({}) }}\n".format(" AND ".join(pairs))

    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("n", type=int, help="number of processes")
    parser.add_argument("formula", type=int, choices=[1, 2, 3],
        help="formula to generate (1: A[]F, 2: E[]F, 3: AG mutex)")
    args = parser.parse_args()

    print(generate(args.n, args.formula))


if __name__ == "__main__":
    main()
