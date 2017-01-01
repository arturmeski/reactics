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

    def enc_reactants_ids(self, level, set_of_ids):
        """Encodes reactants given by their ids in RS"""
        
        enc_ents = True
        for r_id in set_of_ids:
            enc_ents = simplify(And(enc_ents, self.v[level][r_id]))
        return enc_ents
        
    def enc_inhibitors_ids(self, level, set_of_ids):
        """Encodes inhibitors given by their ids in RS"""
        
        enc_ents = True
        for i_id in set_of_ids:
            enc_ents = simplify(And(enc_ents, Not(self.v[level][i_id])))
        return enc_ents

    def enc_context_single_transition(self, level, automaton, transition):
        """"""
        
        src_id, act_ids, (r_ids, i_ids, p_ids), dst_id = transition
        
        enc_transition = self.v_canet_states[level][automaton] == src_id
        enc_transition = simplify(And(enc_transition, self.enc_reactants_ids(level, r_ids), self.enc_inhibitors_ids(level, i_ids)))
        enc_transition = simplify(And(enc_transition, self.v_canet_states[level+1][automaton] == dst_id))
        # ACTIONS NOT ENCODED!
        
        print(enc_transition)
        return enc_transition

    def enc_context_entity_production(self, level, entity):
        """Encodes the automata transitions and the production for a given entity"""
        
        enc_production = False
        
        actions_producing_ent = self.canet.get_actions_producing_entity(entity)
        enc_prod_action = False
        
        for act in actions_producing_ent:
        
            # automata_with_act = self.canet.get_automata_with_action(act)
            enc_aut_with_act = True
            
            for aut_id in self.canet.automata_ids:
                
                aut = self.canet.automata[aut_id]

                t_producing_entity = aut.get_transitions_producing_entity(entity)
                
                enc_t_producing_entity = False
                
                if t_producing_entity:
                    # for the automata that produce the entity we take
                    # all the transitions that produce it:
                    
                    
                    for t in t_producing_entity:
                        enc_t_producing_entity = simplify(Or(enc_t_producing_entity, self.enc_context_single_transition(level, aut_id, t)))

                else:
                    # for all the automata that do not produce the entity
                    # we encode the transitions that synchronise with the action:

                    pass
                    
                enc_aut_with_act = simplify(And(enc_aut_with_act, enc_t_producing_entity))

            enc_prod_action = simplify(Or(enc_prod_action, enc_aut_with_act))
            
        # TODO
        # for aut in remaining_automata_which_do_not_contain_act:
        #      encode no change        

        enc_production = enc_prod_action

        return enc_production

    def enc_automaton_trans(self, level):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = True
                
        prod_context = self.canet.prod_entities
        never_produced_context = self.rs.set_of_bgset_ids - prod_context
        
        # (1) producible entities:
        for ent in prod_context:
            enc_trans = simplify(And(enc_trans, self.enc_context_entity_production(level, ent)))


        # (2) entities that are never produced:

        # (3) TODO: no entity, empty set of entities: transitions with no entities
        # simplify((enc_trans, self.enc_context_no_entity_production(level)))
        # TRANSITIONS PRODUCING EMPTY SETS

        print(enc_trans)
        
        return enc_trans

    def check_reachability(self, state, print_witness=True, print_time=True, print_mem=True):
        """The main method for checking reachability"""
    
        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        current_level = 0
        self.prepare_all_variables()
        self.prepare_all_variables()
        self.prepare_all_variables()
        self.prepare_all_variables()
        
        print(self.enc_automaton_trans(0))

