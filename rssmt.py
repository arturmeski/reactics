#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

from rctsys import ReactionSystem,ReactionSystemWithConcentrations
from smtchecker import SmtChecker
from smtcheckerpgrs import SmtCheckerPGRS
from smtcheckerdistribrs import SmtCheckerDistribRS
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

    r.add_reaction([("a",1)],[("b",2)],[("c",1)])
    r.show()

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

