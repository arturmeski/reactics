from rs import *
from smt import *
import rs_examples 

def run_tests():
    
    test_extended_automaton()
    # process()

def test_extended_automaton():
    
    r = ReactionSystem()
    r.add_bg_set_entity("inc")
    r.add_bg_set_entity("dec")

    c1 = ExtendedContextAutomaton(r)
    c1.add_init_state("init")
    c1.name = "catest"
    c1.add_state("working")
    c1.add_action("act1")
    c1.add_action("act2")
    c1.add_transition("init", ["act1", "act2"], ([],[],["inc"]), "working")
    c1.add_transition("working", ["act2"], ([],[],["inc"]), "working")

    c2 = ExtendedContextAutomaton(r)
    c2.add_init_state("init")
    c2.name = "cxxxx"
    c2.add_state("working")
    c2.add_action("act1")
    c2.add_action("act2")
    c2.add_transition("init", ["act1", "act2"], ([],[],["inc"]), "working")
    c2.add_transition("working", ["act2"], ([],[],["inc"]), "working")

    na = NetworkOfContextAutomata([c1,c2])

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
