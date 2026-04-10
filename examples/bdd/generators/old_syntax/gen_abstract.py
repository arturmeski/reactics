#!/usr/bin/env python3
"""
Generator for the Abstract Pipeline benchmark.

Produces a reaction system modelling a pipeline of N modules,
each cycling through entities a -> y,b -> c -> d before passing
activation to the next module. The final reaction requires all
modules to have completed (all y_i present).

NOTE: generates old-syntax input (context-entities, initial-contexts,
rsctl-property) which is not compatible with the current parser.
"""

import argparse


def generate(n, variant):
    out = "reactions {\n"
    out += "\t{ {x},{s} -> {a1} };\n"

    for i in range(1, n + 1):
        out += "\t{{ {{a{i}}},{{s}} -> {{y{i}}} }};\n".format(i=i)
        out += "\t{{ {{a{i}}},{{s}} -> {{b{i}}} }};\n".format(i=i)
        out += "\t{{ {{b{i}}},{{s}} -> {{c{i}}} }};\n".format(i=i)
        out += "\t{{ {{c{i}}},{{s}} -> {{d{i}}} }};\n".format(i=i)
        out += "\t{{ {{d{i},y{i}}},{{s}} -> {{a{j}}} }};\n".format(i=i, j=i + 1)
        out += "\t{{ {{y{i}}},{{s}} -> {{y{i}}} }};\n".format(i=i)

    final_reactants = "a" + str(n + 1)
    for i in range(1, n + 1):
        final_reactants += ",y" + str(i)
    out += "\t{{ {{{r}}},{{s}} -> {{r}} }};\n".format(r=final_reactants)
    out += "}\n"

    if variant == 1:
        out += "context-entities { s }\n"
    elif variant == 2:
        ctx = "s"
        for i in range(1, n + 1):
            if i % 2 == 0:
                ctx += ",a" + str(i)
        out += "context-entities {{ {} }}\n".format(ctx)

    out += "initial-contexts { {x} }\n"
    out += "rsctl-property { E[{}]F(r) }\n"

    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("n", type=int, help="number of pipeline modules")
    parser.add_argument("variant", type=int, choices=[1, 2],
        help="context variant (1: minimal, 2: extended)")
    args = parser.parse_args()

    print(generate(args.n, args.variant))


if __name__ == "__main__":
    main()
