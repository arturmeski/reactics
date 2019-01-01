#!/usr/bin/env python

from rs import *
from smt import *
from logics import *
from rsltl_shortcuts import *

def gen_expr():
    
    prs = ReactionSystemWithConcentrationsParam()
    
    entities = ["a", "b", "c", "h"]

    for ent in entities:
        prs.add_bg_set_entity((ent, 3))

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

    print("......")
    
    # cprs is defined in the SMT checker    

    # reach_y = ltl_F(bag_entity("h") == 0, "y")
    # reach_yp = ltl_F(bag_entity("h") == 0, "yp")
    # reach_Y = ltl_F(bag_entity("h") == 0, "Y")
    #


    # # rules
    # phi_c1 = ltl_G(bag_entity("h") == 0, ltl_Implies(
    #     bag_entity("y") > 0,
    #     ltl_X(True, bag_And(bag_entity("y") > 0, bag_entity("yp") > 0))))
    #
    # phi_c2 = ltl_G(bag_entity("h") == 0, ltl_Implies(
    #     bag_And(bag_entity("y") > 0, bag_entity("yp") > 0),
    #     ltl_F(True, bag_entity("Y") > 0)))
    #
    # # delayed_Y = ltl_X(True, ltl_And(bag_entity("Y") == 0, ltl_X(True, bag_entity("Y") == 0)))
    #
    # # delayed_Y = ltl_X(True, bag_entity("Y") == 0)
    #
    # delayed_Q = ltl_And(bag_entity("Q") == 0, ltl_X(True, ltl_And(bag_entity("Q") == 0, ltl_X(True, ltl_And(bag_entity("Q") == 0, ltl_F(True, bag_entity("Q") > 0))))))
    #
    # obs_1 = ltl_And(phi_r, phi_c1, phi_c2, delayed_Q)
    
    # obs_2 = ltl_And(f_y2, reach_y, reach_Y, delayed_Y, delayed_Q)

    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))
    #
    
    pc = param_entity(lda, "a") == 0
    f = ltl_F(bag_entity("h") == 0, "c")

    checker = SmtCheckerRSCParam(crprs, optimise=True)
    checker.check_rsltl(formulae_list=[f], param_constr=pc)
    

gen_expr()



