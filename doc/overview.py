#!/usr/bin/env python

from rs import *
from smt import *
from logics import *
from rsltl_shortcuts import *

def ex():
    
    prs = ReactionSystemWithConcentrationsParam()
    
    ent_with_conc = [("a", 3), ("b",2), ("c",1), ("h",1)]

    for ec in ent_with_conc:
        prs.add_bg_set_entity(ec)

    lda = prs.get_param("lda")
    
    prs.add_reaction([("a",1)],[("h",1)],[("b", 2)])
    prs.add_reaction(lda,[("h",1)],[("c",1)])
    
    ##

    ca = ContextAutomatonWithConcentrations(prs)
    ca.add_init_state("0")
    ca.add_state("1")
    
    ca.add_transition("0", [("a", 3)], "1")
    ca.add_transition("1", [], "1")
    ca.add_transition("1", [("h", 1)], "1")

    crprs = ReactionSystemWithAutomaton(prs, ca)
    crprs.show()

    pc = param_entity(lda, "a") == 0
    f = ltl_F(bag_entity("h") == 0, "c")

    checker = SmtCheckerRSCParam(crprs, optimise=True)
    checker.check_rsltl(formulae_list=[f], param_constr=pc)
    
if __name__ == "__main__":
	ex()

# EOF
