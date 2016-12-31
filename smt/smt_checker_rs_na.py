"""
SMT-based Model Checking Module for RS with Context Automaton
"""

from z3 import *
from time import time
from sys import stdout
import resource

from smt.smt_checker_rs import SmtCheckerRS 

class SmtCheckerRSNA(SmtCheckerRS):
    """SMT-based Model Checking for Reaction Systems with Network of Automata"""

    def __init__(self, reaction_system_with_netaut):
        
        self.rs = reaction_system_with_netaut.rs
        self.canet = reaction_system_with_netaut.cas

        self.number_of_automata = self.canet.number_of_automata

        self.v = []
        self.v_ctx = []
        self.v_canet_states = []
        self.v_canet_actions = []
        self.next_level_to_encode = 0

        self.solver = Solver()
        
        self.verification_time = None
        
    def prepare_context_controller_variables(self):
        """Encodes all the state variables"""

        level = self.next_level_to_encode

        ca_states = []
        for ca_id in range(self.number_of_automata):
            ca_states.append(Int("CA"+str(level)+"_a"+str(ca_id)+"_state"))
        self.v_canet_states.append(ca_states)

        # We do not encode actions when there are no transitions needed.
        if level > 0:
            ca_actions = []
            for ca in self.canet.automata:
                 for act_id in range(ca.number_of_actions):
                     ca_actions.append(Bool("CA"+str(level-1)+"_a"+str(self.canet.automata.index(ca))+"_act"+str(act_id)))
            self.v_canet_actions.append(ca_actions)

    def enc_context_controller_init_state(self, level):
        """Encodes the initial state for the network of automata"""

        canet_init_state_enc = True
        for ca_idx in range(self.number_of_automata):
            ca_init_state_enc = self.v_canet_states[level][ca_idx] == self.canet.automata[ca_idx].get_init_state_id()
            canet_init_state_enc = simplify(And(canet_init_state_enc, ca_init_state_enc))

        return canet_init_state_enc
        
    def enc_transition_relation(self, level):
        return simplify(And(self.enc_rs_trans(level), self.enc_automaton_trans(level)))

    def enc_automaton_trans(self, level):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = True
                
        prod_context = self.canet.prod_entities
        never_produced_context = self.rs.set_of_bgset_ids - prod_context
        
        # producible entities:
        for ent in prod_context:
            actions_producing_ent = self.canet.get_actions_producing_entity(ent)            
            for act in actions_producing_ent:
                automata_with_act = self.canet.get_automata_with_action(act)
                for aut_id in automata_with_act:
                    aut = self.canet.automata[aut_id]

        # entities that are never produced:
        
        return enc_trans

    def check_reachability(self, state, print_witness=True, print_time=True, print_mem=True):
    
        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        current_level = 0
        self.prepare_all_variables()
        self.prepare_all_variables()
        self.prepare_all_variables()
        self.prepare_all_variables()
        
        print(self.enc_automaton_trans(0))

