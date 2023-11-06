#!/usr/bin/env python
#
# Copyright (c) 2015-2019 Artur Meski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from rs import *
from smt import *
from logics import *
from rsltl_shortcuts import *

from itertools import chain, combinations

import sys
import resource


def generate_system(chainLen, maxConc):
    """
    This function generates the reaction system with concentrations
    for the scalable chain benchmark

    chainLen is the length of the chain
    maxConc is the maximal concentration
    """

    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("inc", 1))
    r.add_bg_set_entity(("dec", 1))

    for i in range(1, chainLen + 1):
        r.add_bg_set_entity(("e_" + str(i), maxConc))

    for i in range(1, chainLen + 1):
        ent = "e_" + str(i)
        r.add_reaction_inc(ent, "inc", [(ent, 1)], [(ent, maxConc)])
        r.add_reaction_dec(ent, "dec", [(ent, 1)], [])
        if i < chainLen:
            r.add_reaction([(ent, maxConc)], [], [("e_" + str(i + 1), 1)])

    r.add_reaction(
        [("e_" + str(chainLen), maxConc)],
        [("dec", 1)],
        [("e_" + str(chainLen), maxConc)],
    )

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1", 1), ("inc", 1)], "working")
    c.add_transition("working", [("inc", 1)], "working")

    rc = ReactionSystemWithAutomaton(r, c)

    return rc


def generate_formula(formula_number, chainLen, maxConc):
    """
    This function generates the rsLTL formula
    corresponding to the formula_number parameter
    """

    if formula_number == 1:
        ret = Formula_rsLTL.f_F(
            BagDescription.f_entity("inc") > 0,
            (BagDescription.f_entity("e_" + str(chainLen)) >= maxConc),
        )

    elif formula_number == 2:
        f_tmp = Formula_rsLTL.f_F(
            BagDescription.f_entity("inc") > 0,
            (BagDescription.f_entity("e_" + str(chainLen)) == maxConc),
        )
        for i in range(chainLen - 1, 0, -1):
            f_tmp = Formula_rsLTL.f_F(
                BagDescription.f_entity("inc") > 0,
                f_tmp & (BagDescription.f_entity("e_" + str(i)) == maxConc),
            )
        ret = f_tmp

    elif formula_number == 3:
        ret = Formula_rsLTL.f_G(
            BagDescription.f_TRUE(),
            Formula_rsLTL.f_Implies(
                (BagDescription.f_entity("e_1") == 1),
                Formula_rsLTL.f_F(
                    BagDescription.f_entity("inc") > 0,
                    (BagDescription.f_entity("e_" + str(chainLen)) == maxConc),
                ),
            ),
        )

    elif formula_number == 4:
        ret = Formula_rsLTL.f_F(
            BagDescription.f_entity("inc") > 0,
            BagDescription.f_entity("e_1") == maxConc,
        )

    elif formula_number == 5:
        ret = Formula_rsLTL.f_X(
            BagDescription.f_TRUE(),
            Formula_rsLTL.f_U(
                BagDescription.f_entity("inc") > 0,
                BagDescription.f_entity("e_1") > 0,
                BagDescription.f_entity("e_2") > 0,
            ),
        )

    else:
        ret = None

    assert ret is not None, "Unknown formula"

    return ret


def save_statistics(smt_rsc, formula_number, chainLen, maxConc):
    """
    Saves the statistics fetched from smt_rsc into files
    """
    time = 0
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
    filename_t = "bench_rsc_F" + str(formula_number) + "_time.log"
    filename_m = "bench_rsc_F" + str(formula_number) + "_mem.log"
    time = smt_rsc.get_verification_time()

    f = open(filename_t, "a")
    log_str = "(" + str(chainLen) + "," + str(maxConc) + "," + str(time) + ")\n"
    f.write(log_str)
    f.close()

    f = open(filename_m, "a")
    log_str = "(" + str(chainLen) + "," + str(maxConc) + "," + str(mem_usage) + ")\n"
    f.write(log_str)
    f.close()


def scalable_chain(print_system=False):
    """
    This is the entry point for the benchmark
    """
    if len(sys.argv) < 1 + 3:
        print("arguments: <chainLen> <maxConc> <formulaNumber>")
        exit(1)

    chainLen = int(sys.argv[1])  # chain length
    maxConc = int(sys.argv[2])  # depth (max concentration)
    formula_number = int(sys.argv[3])

    if chainLen < 1 or maxConc < 1:
        print("be reasonable")
        exit(1)
    if not formula_number in range(1, 5 + 1):
        print("formulaNumber must be in 1..5")
        exit(1)

    # Generate the reaction systems with concentrations
    rc = generate_system(chainLen, maxConc)

    # Generate the formula
    form = generate_formula(formula_number, chainLen, maxConc)

    # Optional dump/print of the system
    if print_system:
        rc.show()

    # Create an instance of the SMT checker for RS with concentrations
    smt_rsc = SmtCheckerRSC(rc)

    # Start the verification process
    smt_rsc.check_rsltl(formula=form)

    save_statistics(smt_rsc, formula_number, chainLen, maxConc)


def main():
    scalable_chain(print_system=True)


if __name__ == "__main__":
    main()
