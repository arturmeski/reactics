from rs import *
from smt import *
import rs_examples 
from logics import *
from rsltl_shortcuts import *

from itertools import chain, combinations

import sys
import resource

def powerset(iterable,N=None):
    if N is None:
        N = len(s)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(N+1))

def run_tests(cmd_args):
    
    # test_extended_automaton()
    # process()
    # heat_shock_response()
    # scalable_chain(print_system=True)
    # example44()
    # example44_param()
    # heat_shock_response_param(cmd_args)
    # simple_param(cmd_args)

    # param_gene_expression(cmd_args)

def param_gene_expression(cmd_args):
    """
    Simple gene expression example with parameters
    """
    r = ReactionSystemWithConcentrationsParam()

    r.add_bg_set_entity(("x", 1))
    r.add_bg_set_entity(("xp", 1))
    r.add_bg_set_entity(("X", 1))    
    r.add_bg_set_entity(("y", 1))
    r.add_bg_set_entity(("yp", 1))
    r.add_bg_set_entity(("Y", 1))
    r.add_bg_set_entity(("h", 1))
    r.add_bg_set_entity(("Q", 1))

    all_entities = set(r.background_set)

    lda0 = r.get_param("lda0")
    lda1 = r.get_param("lda1")
    lda2 = r.get_param("lda2")
    lda3 = r.get_param("lda3")

    r.add_reaction([("x",1)],[("h",1)],[("x",1)])
    # r.add_reaction([("x",1)],[("h",1)],[("xp",1)])
    r.add_reaction(lda0, [("h",1)],[("xp",1)])
    r.add_reaction([("x",1),("xp",1)],[("h",1)],[("X",1)])

    r.add_reaction([("X",1),("Y",1)],[("h",1)],[("Q",1)])

    ## y
    # r.add_reaction([("y",1)],[("h",1)],[("y",1)])
    # r.add_reaction([("y",1)],[("Q",1)],[("yp",1)])
    # r.add_reaction([("y",1),("yp",1)],[("h",1)],[("Y",1)])

    r.add_reaction([("y",1)],[("h",1)],lda1)
    r.add_reaction(lda2,[("h",1)],[("yp",1)])
    r.add_reaction([("y",1),("yp",1)],[("h",1)],lda3)

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    
    # the experiments starts with adding x and y:
    c.add_transition("0", [("y", 1),("x",1)], "1")
    
    # for all the remaining steps we have empty context sequences
    c.add_transition("1", [], "1")
    c.add_transition("1", [("h", 1)], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    
    # f_x1 = ltl_G(True, ltl_Implies(
    #     exact_state(["x"], all_entities),
    #     ltl_X(bag_And(bag_Not("Y"), bag_Not("Z"), bag_Not("h")), exact_state(["x", "xp"], all_entities))))
    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))

    # reachability
    reach_y = ltl_F(bag_entity("h") == 0, "y")
    reach_yp = ltl_F(bag_entity("h") == 0, "yp")
    reach_Y = ltl_F(bag_entity("h") == 0, "Y")
    #
    phi_r = ltl_And(reach_y, reach_yp, reach_Y)

    # rules
    phi_c1 = ltl_G(bag_entity("h") == 0, ltl_Implies(
        bag_entity("y") > 0,
        ltl_X(True, bag_And(bag_entity("y") > 0, bag_entity("yp") > 0))))

    phi_c2 = ltl_G(bag_entity("h") == 0, ltl_Implies(
        bag_And(bag_entity("y") > 0, bag_entity("yp") > 0),
        ltl_F(True, bag_entity("Y") > 0)))

    # delayed_Y = ltl_X(True, ltl_And(bag_entity("Y") == 0, ltl_X(True, bag_entity("Y") == 0)))

    # delayed_Y = ltl_X(True, bag_entity("Y") == 0)  
    
    delayed_Q = ltl_And(bag_entity("Q") == 0, ltl_X(True, ltl_And(bag_entity("Q") == 0, ltl_X(True, ltl_And(bag_entity("Q") == 0, ltl_F(True, bag_entity("Q") > 0))))))

    obs_1 = ltl_And(phi_r, phi_c1, phi_c2, delayed_Q)
    
    # Observation related to A_x:
    obs_2 = ltl_G(bag_entity("h") == 0, ltl_Implies(
            bag_entity("x") > 0,
            ltl_X(True, bag_And(bag_entity("x") > 0, bag_entity("xp") > 0))))
    
    
    # obs_2 = ltl_And(f_y2, reach_y, reach_Y, delayed_Y, delayed_Q)

    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))
    #
    
    related_to_x = ["x", "xp", "X"]
    related_to_y = ["y", "yp", "Y"]
    params_for_x = [lda0]
    params_for_y = [lda1, lda2, lda3]
    
    
    
    no_x_in_y = param_True()
    for par in params_for_y:
        for ent in related_to_x:
            no_x_in_y = param_And(no_x_in_y, param_entity(par, ent) == 0)
    
    no_y_in_x = param_True()
    for par in params_for_x:
        for ent in related_to_y:
            no_y_in_x = param_And(no_y_in_x, param_entity(par, ent) == 0)
    
    # param_constr = param_And(param_entity(lda3, "Y") > 0, param_entity(lda3, "X") == 0, param_entity(lda2, "Q") == 0, param_entity(lda1, "yp") == 0, param_entity(lda1, "Y") == 0)
    param_constr = param_And(no_y_in_x, no_x_in_y)
        
    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    #
    smt_rsc.check_rsltl(
        formulae_list=[obs_1,obs_2],
        param_constr=param_constr,
    ) #, max_level=4, cont_if_sat=True)


def gene_expression_full(cmd_args):
    """
    Simple gene expression example
    """
    r = ReactionSystemWithConcentrationsParam()
    
    r.add_bg_set_entity(("x", 1))
    r.add_bg_set_entity(("xp", 1))
    r.add_bg_set_entity(("X", 1))

    r.add_bg_set_entity(("y", 1))
    r.add_bg_set_entity(("yp", 1))
    r.add_bg_set_entity(("Y", 1))
    
    r.add_bg_set_entity(("z", 1))
    r.add_bg_set_entity(("zp", 1))
    r.add_bg_set_entity(("Z", 1))
    
    r.add_bg_set_entity(("h", 1))
    r.add_bg_set_entity(("Q", 1))
    r.add_bg_set_entity(("U", 1))

    all_entities = set(r.background_set)
    
    r.add_reaction([("x",1)],[("h",1)],[("x",1)])
    r.add_reaction([("x",1)],[("h",1)],[("xp",1)])    
    r.add_reaction([("x",1),("xp",1)],[("h",1)],[("X",1)])

    ## y
    # r.add_reaction([("y",1)],[("h",1)],[("y",1)])
    # r.add_reaction([("y",1)],[("Q",1)],[("yp",1)])
    # r.add_reaction([("y",1),("yp",1)],[("h",1)],[("Y",1)])
    lda1 = r.get_param("lda1")
    lda2 = r.get_param("lda2")
    lda3 = r.get_param("lda3")
    r.add_reaction([("y",1)],[("h",1)],lda1)
    r.add_reaction(lda2,[("Q",1)],[("yp",1)])
    r.add_reaction([("y",1),("yp",1)],[("h",1)],lda3)

    r.add_reaction([("z",1)],[("h",1)],[("z",1)])
    r.add_reaction([("z",1)], [("X",1)], [("zp",1)])
    r.add_reaction([("z",1),("zp",1)],[("h",1)],[("Z",1)])

    r.add_reaction([("U",1),("X",1)],[("h",1)],[("Q",1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    
    # the experiments starts with adding x and y:
    c.add_transition("0", [("x", 1),("y", 1)], "1")
    
    # for all the remaining steps we have empty context sequences
    c.add_transition("1", [], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    
    # f_x1 = ltl_G(True, ltl_Implies(
    #     exact_state(["x"], all_entities),
    #     ltl_X(bag_And(bag_Not("Y"), bag_Not("Z"), bag_Not("h")), exact_state(["x", "xp"], all_entities))))
    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))

    reach_yp = ltl_F(True, "yp")
    reach_Y = ltl_F(True, "Y")
    reach_y = ltl_F(True, "y")

    f_y1 = ltl_G(bag_entity("h") == 0, ltl_Implies(
        bag_And(bag_entity("Q") == 0, bag_entity("y") > 0),
        ltl_X(True, bag_And(bag_entity("y") > 0, bag_entity("yp") > 0))))

    f_y2 = ltl_G(bag_entity("h") == 0, ltl_Implies(
        bag_And(bag_entity("y") > 0, bag_entity("yp") > 0),
        ltl_F(True, bag_entity("Y") > 0)))

    obs_1 = ltl_And(f_y1, reach_y)
    obs_2 = ltl_And(f_y2, reach_y, reach_Y)

    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))
    #
        
    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    #
    smt_rsc.check_rsltl(formulae_list=[obs_1, obs_2], max_level=3, cont_if_sat=True)

    # smt_rsc.check_rsltl(formula=f_x1, print_witness=True)
    
    
def trivial_param():

    r = ReactionSystemWithConcentrationsParam()
    r.add_bg_set_entity(("x", 3))
    r.add_bg_set_entity(("c", 3))
    r.add_bg_set_entity(("final", 1))
    
    param_p1 = r.get_param("P1")

    r.add_reaction(param_p1, [("c", 1)], [("final", 1)])
    # r.add_reaction([("x", 1)], [("c", 1)], [("final", 1)])
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("x", 1)], "1")
    c.add_transition("1", [], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    smt_rsc = SmtCheckerRSCParam(rc)

    f1 = ltl_F(True, bag_entity("final") >= 1)

    # f1 = Formula_rsLTL.f_F(
    #     BagDescription.f_TRUE(),
    #     BagDescription.f_entity("final") >= 1)
    
    #
    # WARNING: depth limit is set
    #
    smt_rsc.check_rsltl(formula=f1, max_level=10, print_witness=True)


def simple_param(cmd_args):

    r = ReactionSystemWithConcentrationsParam()
    r.add_bg_set_entity(("x", 3))
    r.add_bg_set_entity(("y", 3))
    r.add_bg_set_entity(("c", 3))
    r.add_bg_set_entity(("z", 3))
    r.add_bg_set_entity(("final", 1))
    
    param_p1 = r.get_param("P1")

    r.add_reaction([("x", 1)], [("c", 1)], [("y", 2)])
    # r.add_reaction([("y", 1)], [("c", 1)], [("z", 1)])
    r.add_reaction([("y", 1)], [("c", 1)], r.get_param("P2"))
    r.add_reaction(param_p1, [("x", 1)], [("final", 1)])
    # r.add_reaction([("z", 1)], [("x", 1)], [("final", 1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("x", 1)], "1")
    c.add_transition("1", [], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    
    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)

    f1 = Formula_rsLTL.f_F(
        BagDescription.f_TRUE(),
        BagDescription.f_entity("final") >= 1)
    
    #
    # WARNING: depth limit is set
    #
    smt_rsc.check_rsltl(formula=f1, max_level=10, print_witness=True, cont_if_sat=False)


def heat_shock_response_param(cmd_args, print_system=True):

    stress_temp = 42
    max_temp = 50
    
    r = ReactionSystemWithConcentrationsParam()
    r.add_bg_set_entity(("hsp",1))
    r.add_bg_set_entity(("hsf",1))
    r.add_bg_set_entity(("hsf2",1))
    r.add_bg_set_entity(("hsf3",1))
    r.add_bg_set_entity(("hse",1))
    r.add_bg_set_entity(("mfp",1))
    r.add_bg_set_entity(("prot",1))
    r.add_bg_set_entity(("hsf3:hse",1))
    r.add_bg_set_entity(("hsp:mfp",1))
    r.add_bg_set_entity(("hsp:hsf",1))
    r.add_bg_set_entity(("stress",1))
    r.add_bg_set_entity(("no_stress",1))
    
    param_p1 = r.get_param("P1")
    
    r.add_reaction([("hsf",1)],                         [("hsp",1)],        [("hsf3",1)])
    r.add_reaction([("hsf",1),("hsp",1),("mfp",1)],     [],                 [("hsf3",1)])
    r.add_reaction([("hsf3",1)],                        [("hse",1),("hsp",1)],[("hsf",1)])
    r.add_reaction([("hsf3",1),("hsp",1),("mfp",1)],    [("hse",1)],        [("hsf",1)])
    r.add_reaction([("hsf3",1),("hse",1)],              [("hsp",1)],        [("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("mfp",1),("hse",1)],[],           [("hsf3:hse",1)])
    r.add_reaction([("hse",1)],                         [("hsf3",1)],       [("hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("hse",1)],    [("mfp",1)],        [("hse",1)])
    r.add_reaction([("hsf3:hse",1)],                    [("hsp",1)],        [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("mfp",1),("hsf3:hse",1)],[],                 [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsf",1),("hsp",1)],               [("mfp",1)],        [("hsp:hsf",1)])
    r.add_reaction([("hsp:hsf",1),("stress",1)],[],                 [("hsf",1),("hsp",1)])
    r.add_reaction([("hsp:hsf",1)],                     [("stress",1)],[("hsp:hsf",1)])
    r.add_reaction([("hsp",1),("hsf3:hse",1)],          [("mfp",1)],        [("hse",1),("hsp:hsf",1)])
    r.add_reaction([("stress",1),("prot",1)],   [],                     [("mfp",1),("prot",1)])
    r.add_reaction([("prot",1)],                        [("stress",1)], [("prot",1)])
    r.add_reaction([("hsp",1),("mfp",1)],               [],                 [("hsp:mfp",1)])
    r.add_reaction([("mfp",1)],                         [("hsp",1)],        [("mfp",1)])
    r.add_reaction([("hsp:mfp",1)],                     [],                 [("hsp",1),("prot",1)])

    # r.add_reaction_inc("temp", "heat", [("temp",1)],[("temp",max_temp)])
    # r.add_reaction_dec("temp", "cool", [("temp",1)],[])

    # r.add_permanency("temp",[("heat",1),("cool",1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("hsf",1),("prot",1),("hse",1),("no_stress",1)], "1")
    c.add_transition("1", [("stress",1)], "1")
    c.add_transition("1", [("no_stress",1)], "1")
    c.add_transition("1", [], "1")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    # prop_req = [("hsp:hsf",1),("hse",1),("prot",1)]
    # prop_block = [("temp",stress_temp)]
    # prop_req   = [ ("mfp",1) ]
    # prop_block = [ ]
    # prop       = (prop_req,prop_block)
    # rs_prop    = (state_translate_rsc2rs(prop_req),state_translate_rsc2rs(prop_block))
    #
    
    # f_reach_mfp = Formula_rsLTL.f_F(BagDescription.f_TRUE(), (BagDescription.f_entity("mfp") > 0) )
    f_reach_mfp = ltl_F(True, bag_entity("mfp") > 0)

    f_reach_hspmfp = Formula_rsLTL.f_F(BagDescription.f_TRUE(), (BagDescription.f_entity("hsp:mfp") > 0) )
    
    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    
    smt_rsc.check_rsltl(formulae_list=[f_reach_mfp, f_reach_hspmfp])
    
    
    # (1) if we keep increasing the temperature the protein will eventually misfold
    # f_mfp_when_heating = Formula_rsLTL.f_X(BagDescription.f_TRUE(),
    #         Formula_rsLTL.f_F(BagDescription.f_entity("heat") > 0, (BagDescription.f_entity("mfp") > 0) )
    #     )
    # smt_rsc.check_rsltl(formula=f_mfp_when_heating)
    
    # (2) when heating, we finally exceed the stress_temp
    # f_2 = Formula_rsLTL.f_X(BagDescription.f_TRUE(),
    #         Formula_rsLTL.f_F(BagDescription.f_entity("heat") > 0, (BagDescription.f_entity("temp") > stress_temp))
    #     )
    # smt_rsc.check_rsltl(formula=f_2)
    
    # smt_rsc.check_reachability(prop,max_level=40)

def example44_param():

    r = ReactionSystemWithConcentrationsParam()
    r.add_bg_set_entity(("x", 2))
    r.add_bg_set_entity(("y", 4))
    r.add_bg_set_entity(("h", 2))
    r.add_bg_set_entity(("m", 1))

    r.add_reaction([("y", 1), ("x", 1)], [("y", 2), ("h", 1)], [("y", 2)])
    r.add_reaction([("y", 2), ("x", 2)], [("y", 3), ("h", 1)], [("y", 3)])
    r.add_reaction([("y", 3), ("h", 1)], [("y", 4), ("h", 2)], [("y", 4)])
    r.add_reaction([("y", 4), ("h", 1)], [("h", 2)], [("y", 3)])
    r.add_reaction([("y", 4), ("x", 2)], [("h", 1)], [("y", 2)])
    r.add_reaction([("m", 1)], [("y", 3)], [("m", 1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("y", 1), ("m", 1), ("x", 1)], "1")
    c.add_transition("1", [("x", 1)], "1")
    c.add_transition("1", [("x", 1), ("h", 1)], "1")
    c.add_transition("1", [("x", 2)], "1")
    c.add_transition("1", [("x", 2), ("h", 1)], "1")
    c.add_transition("1", [("h", 1)], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    smt_rsc = SmtCheckerRSCParam(rc)

    # Universal property which seems to be true: (holds also existentially)
    f1 = Formula_rsLTL.f_G(BagDescription.f_entity("x") > 0,
                           Formula_rsLTL.f_Implies(
        (BagDescription.f_entity('y') == 2),
        Formula_rsLTL.f_X(
            (BagDescription.f_entity("x") > 1),
            BagDescription.f_entity("y") >= 3
        )
    )
    )

    # lets see if we can find a counterexample to this property:
    neg_f1 = Formula_rsLTL.f_F(BagDescription.f_entity("x") > 0,
                               Formula_rsLTL.f_And(
        (BagDescription.f_entity('y') == 2),
        Formula_rsLTL.f_X(
            (BagDescription.f_entity("x") > 1),
            BagDescription.f_entity("y") < 3
        )
    )
    )

    # we fix the property f1
    # this one holds:
    f2 = Formula_rsLTL.f_G(
        BagDescription.f_entity("x") > 0, Formula_rsLTL.f_Implies(
            (BagDescription.f_entity('y') == 2),
            Formula_rsLTL.f_X(
                (BagDescription.f_entity("x") > 1) &
                (BagDescription.f_entity("h") < 1),
                BagDescription.f_entity("y") >= 3)))

    # neg_f1 = Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_F(BagDescription.f_entity("x") > 0,
    #     Formula_rsLTL.f_And(
    #         (BagDescription.f_entity('y') > 0),
    #         Formula_rsLTL.f_X(
    #             BagDescription.f_entity("x") > 0,
    #             Formula_rsLTL.f_X(
    #                 BagDescription.f_entity("x") > 1,
    #                 BagDescription.f_entity("y") < 3
    #             )
    #         )
    #     )
    # ))
    smt_rsc.check_rsltl(formula=neg_f1)


def example44():

    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("x", 2))
    r.add_bg_set_entity(("y", 4))
    r.add_bg_set_entity(("h", 2))
    r.add_bg_set_entity(("m", 1))

    r.add_reaction([("y", 1), ("x", 1)], [("y", 2), ("h", 1)], [("y", 2)])
    r.add_reaction([("y", 2), ("x", 2)], [("y", 3), ("h", 1)], [("y", 3)])
    r.add_reaction([("y", 3), ("h", 1)], [("y", 4), ("h", 2)], [("y", 4)])
    r.add_reaction([("y", 4), ("h", 1)], [("h", 2)], [("y", 3)])
    r.add_reaction([("y", 4), ("x", 2)], [("h", 1)], [("y", 2)])
    r.add_reaction([("m", 1)], [("y", 3)], [("m", 1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("y", 1), ("m", 1), ("x", 1)], "1")
    c.add_transition("1", [("x", 1)], "1")
    c.add_transition("1", [("x", 1), ("h", 1)], "1")
    c.add_transition("1", [("x", 2)], "1")
    c.add_transition("1", [("x", 2), ("h", 1)], "1")
    c.add_transition("1", [("h", 1)], "1")

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()
    smt_rsc = SmtCheckerRSC(rc)

    # Universal property which seems to be true: (holds also existentially)
    f1 = Formula_rsLTL.f_G(BagDescription.f_entity("x") > 0,
                           Formula_rsLTL.f_Implies(
        (BagDescription.f_entity('y') == 2),
        Formula_rsLTL.f_X(
            (BagDescription.f_entity("x") > 1),
            BagDescription.f_entity("y") >= 3
        )
    )
    )

    # lets see if we can find a counterexample to this property:
    neg_f1 = Formula_rsLTL.f_F(BagDescription.f_entity("x") > 0,
                               Formula_rsLTL.f_And(
        (BagDescription.f_entity('y') == 2),
        Formula_rsLTL.f_X(
            (BagDescription.f_entity("x") > 1),
            BagDescription.f_entity("y") < 3
        )
    )
    )

    # we fix the property f1
    # this one holds:
    f2 = Formula_rsLTL.f_G(
        BagDescription.f_entity("x") > 0, Formula_rsLTL.f_Implies(
            (BagDescription.f_entity('y') == 2),
            Formula_rsLTL.f_X(
                (BagDescription.f_entity("x") > 1) &
                (BagDescription.f_entity("h") < 1),
                BagDescription.f_entity("y") >= 3)))

    # neg_f1 = Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_F(BagDescription.f_entity("x") > 0,
    #     Formula_rsLTL.f_And(
    #         (BagDescription.f_entity('y') > 0),
    #         Formula_rsLTL.f_X(
    #             BagDescription.f_entity("x") > 0,
    #             Formula_rsLTL.f_X(
    #                 BagDescription.f_entity("x") > 1,
    #                 BagDescription.f_entity("y") < 3
    #             )
    #         )
    #     )
    # ))
    smt_rsc.check_rsltl(formula=neg_f1)

    
def heat_shock_response(print_system=True):

    stress_temp = 42
    max_temp = 50
    
    r = ReactionSystemWithConcentrations()    
    r.add_bg_set_entity(("hsp",1))
    r.add_bg_set_entity(("hsf",1))
    r.add_bg_set_entity(("hsf2",1))
    r.add_bg_set_entity(("hsf3",1))
    r.add_bg_set_entity(("hse",1))
    r.add_bg_set_entity(("mfp",1))
    r.add_bg_set_entity(("prot",1))
    r.add_bg_set_entity(("hsf3:hse",1))
    r.add_bg_set_entity(("hsp:mfp",1))
    r.add_bg_set_entity(("hsp:hsf",1))
    r.add_bg_set_entity(("temp",max_temp))
    r.add_bg_set_entity(("heat",1))
    r.add_bg_set_entity(("cool",1))
    
    r.add_reaction([("hsf",1)],                         [("hsp",1)],        [("hsf3",1)])
    r.add_reaction([("hsf",1),("hsp",1),("mfp",1)],     [],                 [("hsf3",1)])
    r.add_reaction([("hsf3",1)],                        [("hse",1),("hsp",1)],[("hsf",1)])
    r.add_reaction([("hsf3",1),("hsp",1),("mfp",1)],    [("hse",1)],        [("hsf",1)])
    r.add_reaction([("hsf3",1),("hse",1)],              [("hsp",1)],        [("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("mfp",1),("hse",1)],[],           [("hsf3:hse",1)])
    r.add_reaction([("hse",1)],                         [("hsf3",1)],       [("hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("hse",1)],    [("mfp",1)],        [("hse",1)])
    r.add_reaction([("hsf3:hse",1)],                    [("hsp",1)],        [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("mfp",1),("hsf3:hse",1)],[],                 [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsf",1),("hsp",1)],               [("mfp",1)],        [("hsp:hsf",1)])
    r.add_reaction([("hsp:hsf",1),("temp",stress_temp)],[],                 [("hsf",1),("hsp",1)])
    r.add_reaction([("hsp:hsf",1)],                     [("temp",stress_temp)],[("hsp:hsf",1)])
    r.add_reaction([("hsp",1),("hsf3:hse",1)],          [("mfp",1)],        [("hse",1),("hsp:hsf",1)])
    r.add_reaction([("temp",stress_temp),("prot",1)],   [],                     [("mfp",1),("prot",1)])
    r.add_reaction([("prot",1)],                        [("temp",stress_temp)], [("prot",1)])
    r.add_reaction([("hsp",1),("mfp",1)],               [],                 [("hsp:mfp",1)])
    r.add_reaction([("mfp",1)],                         [("hsp",1)],        [("mfp",1)])
    r.add_reaction([("hsp:mfp",1)],                     [],                 [("hsp",1),("prot",1)])

    r.add_reaction_inc("temp", "heat", [("temp",1)],[("temp",max_temp)])
    r.add_reaction_dec("temp", "cool", [("temp",1)],[])

    r.add_permanency("temp",[("heat",1),("cool",1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("hsf",1),("prot",1),("hse",1),("temp",35)], "1")
    c.add_transition("1", [("cool",1)], "1")
    c.add_transition("1", [("heat",1)], "1")
    c.add_transition("1", [], "1")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    # prop_req = [("hsp:hsf",1),("hse",1),("prot",1)]
    # prop_block = [("temp",stress_temp)]
    # prop_req   = [ ("mfp",1) ]
    # prop_block = [ ]
    # prop       = (prop_req,prop_block)
    # rs_prop    = (state_translate_rsc2rs(prop_req),state_translate_rsc2rs(prop_block))
    #
    # f_reach_mfp = Formula_rsLTL.f_F(BagDescription.f_TRUE(), (BagDescription.f_entity("mfp") > 0) )
    
    smt_rsc = SmtCheckerRSC(rc)
    
    # (1) if we keep increasing the temperature the protein will eventually misfold
    # f_mfp_when_heating = Formula_rsLTL.f_X(BagDescription.f_TRUE(),
    #         Formula_rsLTL.f_F(BagDescription.f_entity("heat") > 0, (BagDescription.f_entity("mfp") > 0) )
    #     )
    # smt_rsc.check_rsltl(formula=f_mfp_when_heating)
    
    # (2) when heating, we finally exceed the stress_temp
    f_2 = Formula_rsLTL.f_X(BagDescription.f_TRUE(),
            Formula_rsLTL.f_F(BagDescription.f_entity("heat") > 0, (BagDescription.f_entity("temp") > stress_temp))
        )
    smt_rsc.check_rsltl(formula=f_2)
    
    # smt_rsc.check_reachability(prop,max_level=40)

def state_translate_rsc2rs(p):
    return [e[0] + "#" + str(e[1]) for e in p]    

