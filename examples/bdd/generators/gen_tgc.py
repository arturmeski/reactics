#!/usr/bin/env python3
"""
Generator for the Traffic Guard Controller (TGC) benchmark.

Produces a distributed reaction system where N processes compete
for access to a shared resource, governed by a context automaton
with green/red states. Generates RSCTLK properties for liveness,
reachability, and mutual exclusion (epistemic).
"""

import argparse


OPTIONS = "options { use-context-automaton; make-progressive; };\n"

PROC_TEMPLATE = """
    proc{i} {{
        {{{{out}}, {{}} -> {{approach}}}};
        {{{{approach}}, {{req}} -> {{req}}}};
        {{{{allowed}}, {{}} -> {{in}}}};
        {{{{in}}, {{}} -> {{out,leave}}}};
        {{{{req}}, {{in}} -> {{req}}}};
    }};
"""

CA_TEMPLATE = """
context-automaton {{
    states {{ init, green, red }};
    init-state {{ init }};
    transitions {{
{transitions}
    }};
}};
"""

PROPERTY_TEMPLATE = '\nrsctlk-property {{ {name} : {formula} }};\n'


def conj(fmt, indices, sep=" AND "):
    return sep.join(fmt.format(i=i) for i in indices)


def generate(n):
    out = OPTIONS
    out += "\nreactions {\n"
    for i in range(n):
        out += PROC_TEMPLATE.format(i=i)
    out += "};\n"

    indent = 8 * " "
    transitions = ""

    # init -> green: all processes start with 'out'
    transitions += indent + "{ "
    transitions += " ".join("proc{:d}={{out}}".format(i) for i in range(n))
    transitions += " }: init -> green;\n"

    # green -> red: a process requests
    for i in range(n):
        transitions += "{indent}{{ proc{i}={{allowed}} }}: green -> red : proc{i}.req;\n".format(
            indent=indent, i=i)

    # green -> green: no requests pending
    no_req = conj("~proc{i}.req", range(n))
    for i in range(n):
        transitions += "{indent}{{ proc{i}={{}} }}: green -> green : {guard};\n".format(
            indent=indent, i=i, guard=no_req)

    # red -> green: a process leaves
    for i in range(n):
        transitions += "{indent}{{ proc{i}={{}} }}: red -> green : proc{i}.leave;\n".format(
            indent=indent, i=i)

    # red -> red: no process leaves
    no_leave = conj("~proc{i}.leave", range(n))
    for i in range(n):
        transitions += "{indent}{{ proc{i}={{}} }}: red -> red : {guard};\n".format(
            indent=indent, i=i, guard=no_leave)

    out += CA_TEMPLATE.format(transitions=transitions)

    # f1: each process can eventually enter
    f1 = conj("EF( E<proc{i}.allowed>X( proc{i}.in ) )", range(n))
    out += PROPERTY_TEMPLATE.format(name="f1", formula=f1)

    # f2: all processes can simultaneously approach
    f2 = "EF( " + conj("proc{i}.approach", range(n)) + " )"
    out += PROPERTY_TEMPLATE.format(name="f2", formula=f2)

    # f3: mutual exclusion (knowledge)
    others_not_in = conj("~proc{i}.in", range(1, n))
    f3 = "AG( proc0.in IMPLIES K[proc0]({}) )".format(others_not_in)
    out += PROPERTY_TEMPLATE.format(name="f3", formula=f3)

    # f4: mutual exclusion (common knowledge)
    all_agents = conj("proc{i}", range(n), sep=",")
    f4 = "AG( proc0.in IMPLIES C[{}]({}) )".format(all_agents, others_not_in)
    out += PROPERTY_TEMPLATE.format(name="f4", formula=f4)

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
