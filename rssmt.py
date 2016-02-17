#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

from rctsys import ReactionSystem,ReactionSystemWithConcentrations,ContextAutomatonWithConcentrations,ReactionSystemWithAutomaton
from smtchecker import SmtChecker
from smtcheckerpgrs import SmtCheckerPGRS
from smtcheckerdistribrs import SmtCheckerDistribRS
from smtcheckerrsc import SmtCheckerRSC
import sys
import rs_examples

import resource

profiling = False

version = "0.002"
rsmc_banner = """
 *** Reaction Systems SMT-Based Model Checking

 *** Version: """ + version + """
 *** Author:  Artur Męski <meski@ipipan.waw.pl> / <artur.meski@ncl.ac.uk>
"""


def main():
    
    if len(sys.argv) < 1+1:
        print("provide N")
        exit(1)
    
    N=int(sys.argv[1])
        
    print(rsmc_banner)

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

    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entities(["a","b","c","d"])

    r.add_reaction([("c",1)],[("b",2)],[("c",1),("b",1)])
    r.show()
    
    # print(r.get_reactions_by_product())
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("1")
    c.add_transition("1", [("c",1)], "1")
    c.add_transition("1", [("d",2)], "1")
    c.show()

    rc = ReactionSystemWithAutomaton(r,c)

    smt = SmtCheckerRSC(rc)

    smt.check_reachability([('c',1)],print_time=True,max_level=20)

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

