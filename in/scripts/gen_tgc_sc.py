#!/usr/bin/env python

from sys import argv,exit

OPTIONS_STR = """
options { use-context-automaton; }
"""

PROC_STR = """
    proc{:d} {{
        {{{{out}}, {{}} -> {{approach}}}};
        {{{{approach}}, {{req}} -> {{req}}}};
        {{{{allowed}}, {{}} -> {{in}}}};
        {{{{in}}, {{}} -> {{out,leave}}}};
        {{{{req}}, {{in}} -> {{req}}}};
    }};
"""

CA_STR = """
context-automaton {{
    states {{ init, green, red }}
    init-state {{ init }}
    transitions {{
{:s}
    }}
}}
"""

PROPERTY_STR = """
rsctlk-property {{ {:s} : {:s} }}
"""


#################################################################

if len(argv) < 1:
    print("Usage: {:s} <number of processes>".format(argv[0]))
    exit(100)

n = int(argv[1])

assert n > 1, "number of proc must be > 1"

out = ""

out += OPTIONS_STR
out += "reactions {\n"
for i in range(n):
    out += PROC_STR.format(i)
out += "}\n"

transitions = ""

init_trans = 8*" " + "{ "
for i in range(n):
    init_trans += "proc{:d}={{out}} ".format(i)

init_trans += "}: init -> green;\n"

transitions += init_trans

green_no_change_trans = 8*" " + "{ "
for i in range(n):
    green_no_change_trans += "proc{:d}={{}} ".format(i)
green_no_change_trans += "}: green -> green : ~proc0.req"
for i in range(1, n):
    green_no_change_trans += " AND ~proc{:d}.req".format(i)
green_no_change_trans += ";\n"

transitions += green_no_change_trans

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{allowed}} }}: green -> red : proc{:d}.req;\n".format(8*" ", i, i)

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{}} }}: red -> green : proc{:d}.leave;\n".format(8*" ", i, i)

red_no_change_trans = 8*" " + "{ "
for i in range(n):
    red_no_change_trans += "proc{:d}={{}} ".format(i)
red_no_change_trans += "}: red -> red : ~proc0.leave"
for i in range(1, n):
    red_no_change_trans += " AND ~proc{:d}.leave".format(i)
red_no_change_trans += ";\n"

transitions += red_no_change_trans

out += CA_STR.format(transitions)

# f1
formula = "EF( proc0.in )"
for i in range(1, n):
    formula += " AND EF( proc{:d}.in )".format(i)
out += PROPERTY_STR.format("f1",formula)

# f2
subf = "~proc1.in"
for i in range(2, n):
    subf += " AND ~proc{:d}.in".format(i)
formula = "AG( proc0.in IMPLIES K[proc0]({:s}) )".format(subf)

out += PROPERTY_STR.format("f2",formula)

print(out)
