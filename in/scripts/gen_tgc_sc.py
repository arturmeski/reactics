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

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{allowed}} }}: green -> red : proc{:d}.req;\n".format(8*" ", i, i)

no_req_cond = "~proc0.req"
for i in range(1, n):
     no_req_cond += " AND ~proc{:d}.req".format(i)

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{}} }}: green -> green : {:s};\n".format(8*" ", i, no_req_cond)

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{}} }}: red -> green : proc{:d}.leave;\n".format(8*" ", i, i)

no_leave_cond = "~proc0.leave"
for i in range(1, n):
     no_leave_cond += " AND ~proc{:d}.leave".format(i)

for i in range(n):
    transitions += "{:s}{{ proc{:d}={{}} }}: red -> red : {:s};\n".format(8*" ", i, no_leave_cond)

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
