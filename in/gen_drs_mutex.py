#!/usr/bin/env python

from sys import argv,exit

OPTIONS_STR = """
options { use-context-automaton; }
"""
CONTROLLER_STR = """
    ct {
        {{lock},{release} -> {lock}};
        {{req},{} -> {lock}};
    };
"""

PROC_STR = """
    proc{:d} {{
        {{{{out, busy}}, {{}} -> {{req}}}};
        {{{{out}}, {{}} -> {{req}}}};
        {{{{req}}, {{lock}} -> {{in}}}};
        {{{{in}}, {{busy}} -> {{out, release}}}};
        {{{{in, busy}}, {{}} -> {{in}}}};
        {{{{in, lock}}, {{}} -> {{req}}}};
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
rsctlk-property { AG(proc0.in IMPLIES K[proc0](~proc1.in) ) }
"""


#################################################################

if len(argv) < 2:
    print("Usage: {:s} <number of modules>".format(argv[0]))
    exit(100)

n = int(argv[1])

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

out += PROPERTY_STR

print(out)

        # { ct={} proc1={out} }: s0 -> s1;
        # { ct={} proc2={out} }: s0 -> s1;
        
        # { ct={} proc1={} }: s1 -> s1;
        # { ct={} proc2={} }: s1 -> s1;

