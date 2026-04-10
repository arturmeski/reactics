#!/usr/bin/env python3
"""
Generator for the Binary Counter (BC) benchmark.

Produces a reaction system modelling an N-bit binary counter
with increment and decrement operations controlled via context
entities. Generates one of four RSCTL properties.

NOTE: generates old-syntax input (context-entities, initial-contexts,
rsctl-property) which is not compatible with the current parser.
"""

import argparse

K = 8  # constant used by property 3


def generate(n, prop):
    out = "reactions {\n"

    # (1) no dec, no inc: bits persist
    out += "\t# (1) no decrement, no increment\n"
    for j in range(n):
        out += "\t{{{{p{j}}},{{dec,inc}} -> {{p{j}}}}};\n".format(j=j)

    # (2) increment operation
    out += "\n\t# (2) increment operation\n"
    out += "\t{{inc},{dec,p0} -> {p0}};\n"
    for j in range(1, n):
        bits = ",".join("p" + str(k) for k in range(j))
        out += "\t{{{{inc,{bits}}},{{dec,p{j}}} -> {{p{j}}}}};\n".format(bits=bits, j=j)

    out += "\n\t# the more significant bits remain (inc)\n"
    for j in range(n):
        for k in range(j + 1, n):
            out += "\t{{{{inc,p{k}}},{{dec,p{j}}} -> {{p{k}}}}};\n".format(j=j, k=k)

    # (3) decrement operation
    out += "\n\t# (3) decrement operation\n"
    for j in range(n):
        bits = ",".join("p" + str(k) for k in range(j + 1))
        out += "\t{{{{dec}},{{inc,{bits}}} -> {{p{j}}}}};\n".format(bits=bits, j=j)

    out += "\n\t# the more significant bits remain (dec)\n"
    for j in range(n):
        for k in range(j + 1, n):
            out += "\t{{{{dec,p{j},p{k}}},{{inc}} -> {{p{k}}}}};\n".format(j=j, k=k)

    out += "}\n\n"
    out += "context-entities { inc,dec }\n"
    out += "initial-contexts { {} }\n"

    if prop == 1:
        all_neg = " AND ".join("~p" + str(i) for i in range(n))
        all_pos = " AND ".join("p" + str(i) for i in range(n))
        out += "rsctl-property {{ AG(({}) IMPLIES E[{{inc}},{{dec}}]F({})) }}\n".format(
            all_neg, all_pos)
    elif prop == 2:
        all_pos = " AND ".join("p" + str(i) for i in range(n))
        all_neg = " AND ".join("~p" + str(i) for i in range(n))
        out += "rsctl-property {{ AG(({}) IMPLIES A[{{inc}}]X({})) }}\n".format(
            all_pos, all_neg)
    elif prop == 3:
        parts = ["p" + str(i) for i in range(n - K)]
        parts += ["~p" + str(i) for i in range(n - K, n)]
        out += "rsctl-property {{ E[{{inc}}]F({}) }}\n".format(" AND ".join(parts))
    elif prop == 4:
        out += "rsctl-property {{ AG( p{} IMPLIES EF ~p{} ) }}\n".format(n - 1, n - 1)

    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("n", type=int, help="number of bits")
    parser.add_argument("property", type=int, choices=[1, 2, 3, 4],
        help="property to generate (1-4)")
    args = parser.parse_args()

    if args.property == 3 and args.n < K + 1:
        parser.error("n must be >= {} for property 3".format(K + 1))

    print(generate(args.n, args.property))


if __name__ == "__main__":
    main()
