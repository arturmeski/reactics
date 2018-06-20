#!/usr/bin/env python

from sys import argv,exit

OPTIONS_STR = """
options { use-context-automaton; }
"""
CONTROLLER_STR = """
    ct {
        {{lock},{leave} -> {lock}};
        {{req},{} -> {lock}};
    };
"""

PROC_STR = """
    proc{:d} {{
        {{{{out}}, {{}} -> {{approach}}}};
        {{{{approach}}, {{req}} -> {{req}}}};
        {{{{req}}, {{lock}} -> {{in}}}};
        {{{{in}}, {{}} -> {{out,leave}}}};
        {{{{req}}, {{in}} -> {{req}}}};
    }};
"""

CA_STR = """
context-automaton {{
    states {{ s0, s1 }}
    init-state {{ s0 }}
    transitions {{
{:s}
    }}
}}
"""

PROPERTY_STR = """
rsctlk-property {{ {:s} }}
"""


#################################################################

if len(argv) < 2:
    print("Usage: {:s} <number of processes> <property number>".format(argv[0]))
    exit(100)

n = int(argv[1])
f = int(argv[2])

assert n > 1, "number of proc must be > 1"

out = ""

out += OPTIONS_STR
out += "reactions {\n"
out += CONTROLLER_STR
for i in range(n):
    out += PROC_STR.format(i)
out += "}\n"

transitions = ""

init_trans = 8*" " + "{ ct={} "
for i in range(n):
    init_trans += "proc{:d}={{out}} ".format(i)

init_trans += "}: s0 -> s1;\n"

transitions += init_trans

for i in range(n):
    transitions += "{:s}{{ ct={{}} proc{:d}={{}} }}: s1 -> s1;\n".format(8*" ", i)    

out += CA_STR.format(transitions)

if f == 1:
    subf = "~proc1.in"
    for i in range(2, n):
        subf += " AND ~proc{:d}.in".format(i)
    formula = "AG( proc0.in IMPLIES K[proc0]({:s}) )".format(subf)
else:
    assert False, "No such formula"

out += PROPERTY_STR.format(formula)

print(out)

