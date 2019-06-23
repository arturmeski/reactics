#!/usr/bin/env python

from sys import argv,exit

OPTIONS_STR = """
options { use-context-automaton; make-progressive; };
"""

PROC_STR = """
    proc{:d} {{
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

CA_STR = """
context-automaton {{
    states {{ init, act }};
    init-state {{ init }};
    transitions {{
{:s}
    }};
}};
"""

PROPERTY_STR = """
rsctlk-property {{ {:s} : {:s} }};
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
for i in range(1, n+1):
    out += PROC_STR.format(i)

out += FINAL_PROC
out += "};\n"

transitions = ""

init_trans = 8*" " + "{ proc1={a} }: init -> act;\n"
transitions += init_trans

for i in range(1, n+1):
    transitions += "{:s}{{ proc{:d}={{}} }}: act -> act : ~proc{:d}.dy;\n".format(8*" ", i, i, i)

for i in range(2, n+1):
    transitions += "{:s}{{ proc{:d}={{a}} }}: act -> act : proc{:d}.dy;\n".format(8*" ", i, i-1)

final_cond = "proc1.dy"
for i in range(2, n+1):
     final_cond += " AND proc{:d}.dy".format(i)

transitions += "{:s}{{ procFinal={{done}} }}: act -> act : {:s};\n".format(8*" ", final_cond)

out += CA_STR.format(transitions)

# f1
formula = "EF( procFinal.done )"
out += PROPERTY_STR.format("f1",formula)

# f2
formula = "AG( proc{:d}.d IMPLIES K[proc{:d}]( proc{:d}.y ) )".format(n, n, n-1)
out += PROPERTY_STR.format("f2",formula)

# x1
formula = "EF( ~procFinal.done )"
out += PROPERTY_STR.format("x1",formula)

print(out)

