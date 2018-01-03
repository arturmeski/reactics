#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Reaction Systems SMT-Based Model Checking Module

"""

import argparse

from rs import *
from smt import *
import sys
import rs_examples
import rs_testing

from colour import *

profiling = False

if profiling:
    import resource

##################################################################

version = "2017/04/08/00"
rsmc_banner = """
Reaction Systems SMT-Based Model Checking

Version:  """ + version + """
Author:   Artur Meski <meski@ipipan.waw.pl> / <artur.meski@ncl.ac.uk>
"""

##################################################################


def print_banner():
    print()
    for line in rsmc_banner.split("\n"):
        print(colour_str(C_GREEN, " " + 3 * "-" + " "), line)
    print()

##################################################################


def main():
    """Main function"""

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", 
        help="turn verbosity on", action="store_true")
    parser.add_argument("-o", "--optimise", 
        help="minimise the parametric computation result", action="store_true")
    parser.add_argument("-n", "--scaling-parameter",
        help="scaling parameter value (used in some benchmarks)")

    args = parser.parse_args()

    print_banner()
    rs_testing.run_tests(args)

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
