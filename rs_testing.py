from rs import *
from smt import *

def run_tests():
    
    test_extended_automaton()
    # process()

def test_extended_automaton():
    
    r = ReactionSystem()
    r.add_bg_set_entity("inc")
    r.add_bg_set_entity("dec")

    c = ExtendedContextAutomaton(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_action("act1")
    c.add_action("act2")
    c.add_transition("init", ["act1", "act2"], ([],[],["inc"]), "working")
    c.add_transition("working", ["act2"], ([],[],["inc"]), "working")

    rc = ReactionSystemWithAutomaton(r,c)

    rc.show()

def process():
    
    # rs_examples.run_counter_exp()
    rs_examples.chain_reaction(print_system=True)
    # rs_examples.heat_shock_response()
    
    

# PGRS:
# rsca = rs_examples.ca_toy_ex1()
# rsca.show()
# smt = SmtCheckerPGRS(rsca)
# smt.check_reachability(rs_examples.ca_toy_ex1_property1(), print_time=True)

# rsca = rs_examples.ca_bitctr(N)
# rsca.show(True)
# smt = SmtCheckerPGRS(rsca)
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
