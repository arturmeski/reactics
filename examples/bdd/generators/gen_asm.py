#!/usr/bin/env python3
"""
Generator for the Assembly-line (ASM) benchmark.

Produces a distributed reaction system modelling an assembly line
where N sequential processes pass activation tokens. Each process
cycles through entities a -> y,b -> c -> d, and the final process
signals 'done'. Uses a context automaton for scheduling.
"""

import argparse


OPTIONS = "options { use-context-automaton; make-progressive; };\n"

PROC_TEMPLATE = """
    proc{i} {{
        {{{{a}}, {{s}} -> {{y}}}};
        {{{{y}}, {{s}} -> {{y}}}};
        {{{{a}}, {{s}} -> {{b}}}};
        {{{{b}}, {{s}} -> {{c}}}};
        {{{{c}}, {{s}} -> {{d}}}};
        {{{{d,y}}, {{s}} -> {{dy}}}};
    }};
"""

FINAL_PROC = """
    procFinal {
        {{done}, {s} -> {done}};
    };
"""

CA_TEMPLATE = """
context-automaton {{
    states {{ init, act }};
    init-state {{ init }};
    transitions {{
{transitions}
    }};
}};
"""

PROPERTY_TEMPLATE = '\nrsctlk-property {{ {name} : {formula} }};\n'


def generate(n):
    out = OPTIONS
    out += "\nreactions {\n"
    for i in range(1, n + 1):
        out += PROC_TEMPLATE.format(i=i)
    out += FINAL_PROC
    out += "};\n"

    indent = 8 * " "
    transitions = ""

    # init -> act: first process gets activated
    transitions += "{indent}{{ proc1={{a}} }}: init -> act;\n".format(indent=indent)

    # act -> act: process stays idle (dy not produced)
    for i in range(1, n + 1):
        transitions += "{indent}{{ proc{i}={{}} }}: act -> act : ~proc{i}.dy;\n".format(
            indent=indent, i=i)

    # act -> act: next process gets activated when previous produces 'dy'
    for i in range(2, n + 1):
        transitions += "{indent}{{ proc{i}={{a}} }}: act -> act : proc{prev}.dy;\n".format(
            indent=indent, i=i, prev=i - 1)

    # act -> act: final process signals done when all have produced 'dy'
    all_dy = " AND ".join("proc{}.dy".format(i) for i in range(1, n + 1))
    transitions += "{indent}{{ procFinal={{done}} }}: act -> act : {guard};\n".format(
        indent=indent, guard=all_dy)

    out += CA_TEMPLATE.format(transitions=transitions)

    # f1: the assembly line eventually completes
    out += PROPERTY_TEMPLATE.format(name="f1", formula="EF( procFinal.done )")

    # f2: last process knows its predecessor has produced 'y'
    f2 = "AG( proc{n}.d IMPLIES K[proc{n}]( proc{prev}.y ) )".format(n=n, prev=n - 1)
    out += PROPERTY_TEMPLATE.format(name="f2", formula=f2)

    # x1: negation of f1 (sanity check -- should also hold)
    out += PROPERTY_TEMPLATE.format(name="x1", formula="EF( ~procFinal.done )")

    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("n", type=int, help="number of processes (must be > 1)")
    args = parser.parse_args()

    if args.n < 2:
        parser.error("number of processes must be > 1")

    print(generate(args.n))


if __name__ == "__main__":
    main()
