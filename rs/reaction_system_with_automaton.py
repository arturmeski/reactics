from sys import exit
from colour import *

from rs.reaction_system_with_concentrations import ReactionSystemWithConcentrations
from rs.context_automaton_with_concentrations import ContextAutomatonWithConcentrations
from rs.network_of_context_automata import NetworkOfContextAutomata

class ReactionSystemWithAutomaton(object):
    
    def __init__(self, reaction_system, context_automaton):
        self.rs = reaction_system
        self.ca = context_automaton

    def show(self, soft=False):
        self.rs.show(soft)
        self.ca.show()
        
    def is_with_concentrations(self):
        if not isinstance(self.rs, ReactionSystemWithConcentrations):
            return False
        if not isinstance(self.ca, ContextAutomatonWithConcentrations):
            return False
        return True

    def sanity_check(self):
        pass
        
    def get_ordinary_reaction_system_with_automaton(self):
        
        if not self.is_with_concentrations():
            raise RuntimeError("Not RS/CA with concentrations")
        
        ors = self.rs.get_reaction_system()
        oca = self.ca.get_automaton_with_flat_contexts(ors)
        
        return ReactionSystemWithAutomaton(ors, oca)
        
