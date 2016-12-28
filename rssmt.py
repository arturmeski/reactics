#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

from rs import *
from smt import *
import sys
import rs_examples
import rs_testing

from colour import *

import resource

profiling = False

##################################################################    

version = "2016/12/28/00"
rsmc_banner = """Reaction Systems SMT-Based Model Checking

Version: """ + version + """
Author:  Artur Męski <meski@ipipan.waw.pl> / <artur.meski@ncl.ac.uk>"""

##################################################################    

def print_banner():
    print()
    for line in rsmc_banner.split("\n"):
        print(colour_str(C_GREEN, " " + 3*"-" + " "), line)
    print()

##################################################################    

def main():
    """Main function"""
    
    print_banner()
    rs_testing.run_tests()

##################################################################    
    
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

# EOF
