#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

from rctsys import ReactionSystem
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

    #rs = rs_examples.toy_ex3()
    #rs = rs_examples.bitctr(16)
    
    #smt = SmtChecker(rs)
    #smt.check_reachability(["p0","p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15"], print_time=True)
    #smt.check_reachability(["1","3","4"], print_time=True)

    # PGRS:
    # rsca = rs_examples.ca_toy_ex1()
    # rsca.show()
    # smt = SmtCheckerPGRS(rsca)
    # smt.check_reachability(rs_examples.ca_toy_ex1_property1(), print_time=True)

    # Distributed RS:

    drs = rs_examples.drs_mutex(N)
    #drs.show()

    smt = SmtCheckerDistribRS(drs,debug_level=0)
    smt.check_reachability(rs_examples.drs_mutex_property1(N),
        exclusive_state=False,
        max_level=10,
        print_time=True,
        print_mem=True)

    # drs = rs_examples.drs_toy_ex1()
    # drs.show()
    #
    # smt = SmtCheckerDistribRS(drs,debug_level=3)
    # smt.check_reachability(rs_examples.drs_toy_ex1_property1(),max_level=10,print_time=True)

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

