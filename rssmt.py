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

    r.add_bg_set_entity("e")
    r.add_bg_set_entity("inc")    
    r.add_reaction_inc("e",[("e",1),("inc",1)],[("e",N)])
    # for i in range(1,N):
        # r.add_reaction([("e",i),("inc",1)],[("e",N)],[("e",i+1)])
    # r.show()
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")
     # c.show()

    rc = ReactionSystemWithAutomaton(r,c)
    
    rc.show()
    
    smt_rsc = SmtCheckerRSC(rc)    
    smt_rsc.check_reachability([('e',N)],print_time=True,max_level=N)

    # orc = rc.get_ordinary_reaction_system_with_automaton()
    # orc.show()
    # smt_tr_rs = SmtCheckerPGRS(orc)
    # smt_tr_rs.check_reachability(['e_' + str(N)],print_time=True)

    print("Reaction System with Concentrations:", smt_rsc.get_verification_time())
    # print("Reaction System from translating RSC:", smt_tr_rs.get_verification_time())

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

