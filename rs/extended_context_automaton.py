from sys import exit
from colour import *

from rs.context_automaton import ContextAutomaton

class ExtendedContextAutomaton(ContextAutomaton):
    """Extended Context Automaton"""
    def __init__(self, reaction_system):
        self._actions = []
        super(ExtendedContextAutomaton, self).__init__(reaction_system)
    
    def add_transition(self, src, action, ctx_reaction, dst):
        
        ctx_reactants, ctx_inhibitors, ctx_products = ctx_reaction 
        
        if not type(ctx_products) is set and not type(ctx_products) is list:
            print("Contexts set (context products) must be of type set or list")
        
        if not self.is_valid_rs_set(ctx_reactants):
            raise RuntimeError("one of the entities in the reactants set is unknown (undefined)!")
        
        if not self.is_valid_rs_set(ctx_inhibitors):
            raise RuntimeError("one of the entities in the inhibitors set is unknown (undefined)!")
        
        if not self.is_valid_rs_set(ctx_products):
            raise RuntimeError("one of the entities in the context set is unknown (undefined)!")        
        
        if not self.is_state(src):
            raise RuntimeError("\"" + src + "\" is an unknown (undefined) state")

        if not self.is_state(dst):
            raise RuntimeError("\"" + dst + "\" is an unknown (undefined) state")

        src_id = self.get_state_id(src)
        dst_id = self.get_state_id(dst)
        act_id = self.get_action_id(action)
        r_ids = self.get_set_of_ids(ctx_reactants)
        i_ids = self.get_set_of_ids(ctx_inhibitors)
        p_ids = self.get_set_of_ids(ctx_products)
        
        self._transitions.append((src_id, act_id, (r_ids, i_ids, p_ids), dst_id))
    
    def show_transitions(self):
        print(C_MARK_INFO + " Context automaton transitions:")
        for src_id, act_id, reaction, dst_id in self._transitions:
            str_transition = self.get_state_name(src_id) + " --( " 
            str_transition += self.get_action_name(act_id) + " | "
            str_transition += "( " + self.rsset2str(reaction[0]) + "," + self.rsset2str(reaction[1]) + "," + self.rsset2str(reaction[2]) + " )"
            str_transition += " )--> " + self.get_state_name(dst_id)
            print(" - " + str_transition)
    
    def add_action(self, action_name):
        if action_name not in self._actions:
            self._actions.append(action_name)
        else:
            print("\'%s\' already added. skipping..." % (action_name,))
    
    def get_action_id(self, action_name):
        try:
            return self._actions.index(action_name)
        except ValueError:
            print_error("Undefined context automaton action: " + repr(action_name))
            exit(1)
    
    def get_action_name(self, action_id):
        return self._actions[action_id]
                        
    def show_actions(self):
        print(C_MARK_INFO + " Context automaton actions:")
        for act in self._actions:
            print(" - " + act)
    
    def show(self):
        self.show_states()
        self.show_actions()
        self.show_transitions()
