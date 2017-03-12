from rs import *
from smt import *
import rs_examples 
from logics import *

def run_tests():
    
    # test_extended_automaton()
    # process()
    test_rsLTL()
    
def test_rsLTL():

    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("inc",2))
    r.add_bg_set_entity(("ent2",5))
    r.add_reaction([("ent2",1),("inc",1)],[],[("ent2",2)])
    r.add_reaction([("ent2",2)],[],[("ent2",2)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("ent2",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")

    # x = ( Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_bag( ~((BagDescription.f_entity("ent1") == 3) | (BagDescription.f_entity("ent2") < 3)) ) ) ) & Formula_rsLTL.f_X(BagDescription.f_TRUE(), Formula_rsLTL.f_bag( ~((BagDescription.f_entity("ent3") == 1) ) ) )
    # x = Formula_rsLTL.f_G((BagDescription.f_entity("inc") > 0), (BagDescription.f_entity("ent1") == 3) | (BagDescription.f_entity("ent2") < 3))
    
    x = Formula_rsLTL.f_F(BagDescription.f_TRUE(), (BagDescription.f_entity("ent2") == 2) )
    
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
