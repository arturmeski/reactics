#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

from rs import *
from smt import *
import sys
import rs_examples

from colour import *

import resource

profiling = False

version = "2016/12/28/00"
rsmc_banner = """Reaction Systems SMT-Based Model Checking

Version: """ + version + """
Author:  Artur Męski <meski@ipipan.waw.pl> / <artur.meski@ncl.ac.uk>"""

def print_banner():
    print()
    for line in rsmc_banner.split("\n"):
        print(colour_str(C_GREEN, " " + 3*"-" + " "), line)
    print()

def process():
    
    # rs_examples.run_counter_exp()
    rs_examples.chain_reaction(print_system=True)
    # rs_examples.heat_shock_response()

##################################################################    

def main():
    
    print_banner()

    # process()
    r = ReactionSystem()
    r.add_bg_set_entity("inc")
    r.add_bg_set_entity("dec")
    
    c = ExtendedContextAutomaton(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_action("act1")
    c.add_action("act2")
    c.add_transition("init", "act1", ([],[],["inc"]), "working")
    c.add_transition("working", "act2", ([],[],["inc"]), "working")
    
    rc = ReactionSystemWithAutomaton(r,c)

    rc.show()
    
if __name__ == "__main__":
    try:
        if profiling:
            import profile
            profile.run('main()')
        else:
            main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(99)

# PGRS:
# rsca = rs_examples.ca_toy_ex1()
# rsca.show()
# smt = SmtCheckerPGRS(rsca)
# smt.check_reachability(rs_examples.ca_toy_ex1_property1(), print_time=True)

# rsca = rs_examples.ca_bitctr(N)
# rsca.show(True)
# smt = SmtCheckerPGRS(rsca)
# smt.check_reachability(rs_examples.ca_bitctr_property(N), print_time=True)

# Distributed RS:
#drs = rs_examples.drs_mutex(N)
#drs.show()

#smt = SmtCheckerDistribRS(drs,debug_level=0)
#smt.check_reachability(rs_examples.drs_mutex_property1(N),
#    exclusive_state=False,
#    max_level=10,
#    print_time=True,
#    print_mem=True)

# drs = rs_examples.drs_toy_ex1()
# drs.show()
#
# smt = SmtCheckerDistribRS(drs,debug_level=3)
# smt.check_reachability(rs_examples.drs_toy_ex1_property1(),max_level=10,print_time=True)
