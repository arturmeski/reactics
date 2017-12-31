from rs import *
from smt import *
import rs_examples 
from logics import *
from rsltl_shortcuts import *

import sys
import resource

def run_tests(cmd_args):
    
    # test_extended_automaton()
    # process()
    # heat_shock_response()
    # scalable_chain(print_system=True)
    # example44()
    # example44_param()
    # heat_shock_response_param(cmd_args)
    # simple_param(cmd_args)

    gene_expression(cmd_args)

def gene_expression(cmd_args):
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
    r.add_bg_set_entity(("h", 1))
    r.add_bg_set_entity(("Q", 1))

    all_entities = set(r.background_set)

    r.add_reaction([("x",1)],[("h",1)],[("x",1)])
    r.add_reaction([("x",1)],[("h",1)],[("xp",1)])
    r.add_reaction([("x",1),("xp",1)],[("h",1)],[("X",1)])

    r.add_reaction([("X",1),("Y",1)],[("h",1)],[("Q",1)])

    ## y
    # r.add_reaction([("y",1)],[("h",1)],[("y",1)])
    # r.add_reaction([("y",1)],[("Q",1)],[("yp",1)])
    # r.add_reaction([("y",1),("yp",1)],[("h",1)],[("Y",1)])
    lda1 = r.get_param("lda1")
    lda2 = r.get_param("lda2")
    lda3 = r.get_param("lda3")

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
    
    # obs_2 = ltl_And(f_y2, reach_y, reach_Y, delayed_Y, delayed_Q)

    # f_x2 = ltl_G(True, ltl_Implies(
    #     exact_state(["x", "xp"], all_entities),
    #     ltl_X(bag_Not("h"), exact_state("X", all_entities))))
    #
    
    param_constr = param_And(param_entity(lda3, "Y") > 0, param_entity(lda2, "Q") == 0, param_entity(lda1, "yp") == 0, param_entity(lda1, "Y") == 0)
        
    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    #
    smt_rsc.check_rsltl(formulae_list=[obs_1], param_constr=param_constr) #, max_level=4, cont_if_sat=True)

    # smt_rsc.check_rsltl(formula=f_x1, print_witness=True)

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


def scalable_chain(print_system=False):
    
    if len(sys.argv) < 1+3:
        print("arguments: <chainLen> <maxConc> <formulaNumber>")
        exit(1)

    chainLen=int(sys.argv[1]) # chain length
    maxConc=int(sys.argv[2]) # depth (max concentration)
    formula_number=int(sys.argv[3])
        
    if chainLen < 1 or maxConc < 1:
        print("be reasonable")
        exit(1)
    if not formula_number in range(1,5+1):
        print("formulaNumber must be in 1..5")
        exit(1)
    
    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("inc",1))
    r.add_bg_set_entity(("dec",1))
    
    for i in range(1,chainLen+1):
        r.add_bg_set_entity(("e_" + str(i),maxConc))
    
    for i in range(1,chainLen+1):
        ent = "e_" + str(i)
        r.add_reaction_inc(ent, "inc", [(ent, 1)],[(ent,maxConc)])
        r.add_reaction_dec(ent, "dec", [(ent, 1)],[])
        if i < chainLen:
            r.add_reaction([(ent,maxConc)],[],[("e_"+str(i+1),1)])

    r.add_reaction([("e_" + str(chainLen),maxConc)],[("dec",1)],[("e_" + str(chainLen),maxConc)])
        
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")
    
    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    smt_rsc = SmtCheckerRSC(rc)

    if formula_number == 1:
        f_1 = Formula_rsLTL.f_F( BagDescription.f_entity("inc") > 0, (BagDescription.f_entity('e_'+str(chainLen)) >= maxConc) )
        smt_rsc.check_rsltl(formula=f_1)
    elif formula_number == 2:
        f_tmp = Formula_rsLTL.f_F( BagDescription.f_entity("inc") > 0, (BagDescription.f_entity('e_'+str(chainLen)) == maxConc) )
        for i in range(chainLen-1,0,-1):
            f_tmp = Formula_rsLTL.f_F( BagDescription.f_entity("inc") > 0, f_tmp & (BagDescription.f_entity('e_'+str(i)) == maxConc) )
        f_2 = f_tmp
        smt_rsc.check_rsltl(formula=f_2)
    elif formula_number == 3:
        f_3 = Formula_rsLTL.f_G( BagDescription.f_TRUE(),
            Formula_rsLTL.f_Implies(
                (BagDescription.f_entity('e_1') == 1),
                Formula_rsLTL.f_F(
                    BagDescription.f_entity("inc") > 0,
                    (BagDescription.f_entity('e_'+str(chainLen)) == maxConc)
                )
            )
        )
        print(i)
        smt_rsc.check_rsltl(formula=f_3)
    elif formula_number == 4:
        f_4 = Formula_rsLTL.f_F( BagDescription.f_entity("inc") > 0 , BagDescription.f_entity('e_1') == maxConc )
        smt_rsc.check_rsltl(formula=f_4)
        
    elif formula_number == 5:
        f_5 = Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_U( BagDescription.f_entity("inc") > 0 , BagDescription.f_entity('e_1') > 0, BagDescription.f_entity('e_2') > 0 ) )
        smt_rsc.check_rsltl(formula=f_5)
    
    ###########################################################################

    time=0
    mem_usage=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024*1024)
    filename_t="bench_rsc_F" + str(formula_number) + "_time.log"
    filename_m="bench_rsc_F" + str(formula_number) + "_mem.log"
    time=smt_rsc.get_verification_time()

    f=open(filename_t, 'a')    
    log_str="(" + str(chainLen) + "," + str(maxConc) + "," + str(time) + ")\n"
    f.write(log_str)
    f.close()
    
    f=open(filename_m, 'a')
    log_str="(" + str(chainLen) + "," + str(maxConc) + "," + str(mem_usage) + ")\n"
    f.write(log_str)
    f.close()


def test_rsLTL():

    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("inc",2))
    r.add_bg_set_entity(("ent1",1))
    r.add_bg_set_entity(("ent2",5))
    r.add_reaction([("ent2",1),("inc",1)],[],[("ent2",2)])
    r.add_reaction([("ent2",2)],[],[("ent2",2)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("ent2",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")

    # x = ( Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_bag( ~((BagDescription.f_entity("ent1") == 3) | (BagDescription.f_entity("ent2") < 3)) ) ) ) & Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_bag( ~((BagDescription.f_entity("ent3") == 1) ) ) )
    x = Formula_rsLTL.f_G((BagDescription.f_entity("inc") > 0), (BagDescription.f_entity("ent1") == 3) | (BagDescription.f_entity("ent2") < 3))
    
    #x = Formula_rsLTL.f_F(BagDescription.f_TRUE(), (BagDescription.f_entity("ent2") == 2) )
    
    print(x)
    
    rc = ReactionSystemWithAutomaton(r,c)
    rc.show()
    
    checker = SmtCheckerRSC(rc)
    checker.check_rsltl(formula=x)
    
    # checker.dummy_unroll(10)
    # e = rsLTL_Encoder(checker)
    # print(checker.get_loop_encodings())
    # print(e.encode(x, 0, 10))

def test_extended_automaton():
    
    r = ReactionSystem()
    r.add_bg_set_entity("a")
    r.add_bg_set_entity("b")
    r.add_bg_set_entity("inc")
    r.add_bg_set_entity("dec")
    r.add_bg_set_entity("decx")
    r.add_bg_set_entity("baam")

    c1 = ExtendedContextAutomaton(r)
    c1.add_init_state("init")
    c1.name = "catest"
    c1.add_state("working")
    c1.add_action("act1")
    c1.add_action("act2")
    c1.add_transition("init", ["act1", "act2"], (["a"],["b"],["inc","dec"]), "working")
    c1.add_transition("working", ["act2"], ([],[],["inc"]), "working")

    c2 = ExtendedContextAutomaton(r)
    c2.add_init_state("init")
    c2.name = "c2"
    c2.add_state("working")
    c2.add_action("act1")
    c2.add_action("act2")
    c2.add_transition("init", ["act1", "act2"], ([],[],["inc"]), "working")
    c2.add_transition("working", ["act2"], ([],[],["inc"]), "working")
    
    c3 = ExtendedContextAutomaton(r)
    c3.add_init_state("init")
    c3.name = "c3"
    c3.add_state("working")
    c3.add_action("act1")
    c3.add_transition("init", ["act1"], ([],[],["inc"]), "working")
    
    c4 = ExtendedContextAutomaton(r)
    c4.add_init_state("init")
    c4.name = "c4"
    c4.add_state("w")
    c4.add_action("action_x")
    c4.add_transition("init", ["action_x"], ([],[],["baam"]), "w")
    #
    # c4 = ExtendedContextAutomaton(r)
    # c4.add_init_state("init")
    # c4.name = "c4"
    # c4.add_state("working")
    # c4.add_action("act1")
    # c4.add_action("act42")
    # c4.add_transition("init", ["act1", "act42"], ([],[],["inc"]), "working")
    # c4.add_transition("working", ["act42"], ([],[],["inc"]), "working")
    #
    # c5 = ExtendedContextAutomaton(r)
    # c5.add_init_state("init")
    # c5.name = "c5"
    # c5.add_state("working")
    # c5.add_action("act1")
    # c5.add_action("act2")
    # c5.add_transition("init", ["act1", "act2"], ([],[],["inc"]), "working")
    # c5.add_transition("working", ["act2"], ([],[],["inc"]), "working")

    na = NetworkOfContextAutomata(r, [c1,c2,c3,c4])

    rna = ReactionSystemWithNetworkOfAutomata(r,na)

    rna.show()
    
    checker = SmtCheckerRSNA(rna)
    
    checker.check_reachability([])

def process():
    
    # rs_examples.run_counter_exp()
    rs_examples.chain_reaction(print_system=True)
    # rs_examples.heat_shock_response()
    
    

# RS:
# rsca = rs_examples.ca_toy_ex1()
# rsca.show()
# smt = SmtCheckerRS(rsca)
# smt.check_reachability(rs_examples.ca_toy_ex1_property1(), print_time=True)

# rsca = rs_examples.ca_bitctr(N)
# rsca.show(True)
# smt = SmtCheckerRS(rsca)
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
