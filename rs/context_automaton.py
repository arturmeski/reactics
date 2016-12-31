from sys import exit
from colour import *
        
class ContextAutomaton(object):
    
    def __init__(self, reaction_system):
        self._states = []
        self._transitions = []
        self._init_state = None
        self._reaction_system = reaction_system
        self._name = ""
        self._prod_entities = set()
        
    @property
    def states(self):
        return self._states
    
    @property
    def transitions(self):
        return self._transitions
    
    @property
    def prod_entities(self):
        return self._prod_entities
    
    @property
    def reaction_system(self):
        return self._reaction_system
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, automaton_name):
        self._name = automaton_name
        
    def add_state(self, name):
        if name not in self._states:
            self._states.append(name)
        else:
            print("\'%s\' already added. skipping..." % (name,))
    
    def add_states(self, states_set):
        for st in states_set:
            self.add_state(st)
    
    def add_init_state(self, name):
        self.add_state(name)
        self._init_state = self._states.index(name)

    def get_init_state_name(self):
        if self._init_state == None:
            return None
        return self._states[self._init_state]

    def is_state(self, name):
        if name in self._states:
            return True
        else:
            return False

    def get_state_id(self, name):
        try:
            return self._states.index(name)
        except ValueError:
            print_error("Undefined context automaton state: " + repr(name))
            exit(1)

    def get_state_name(self, state_id):
        return self._states[state_id]

    def get_init_state_id(self):
        return self._init_state
    
    def print_states(self):
         for state in self._states:
            print(state)
    
    def is_valid_rs_set(self, elements):
        if set(elements).issubset(self._reaction_system.background_set):
            return True
        else:
            return False
            
    def is_valid_context(self, context):
        return self.is_valid_rs_set(context)
        
    def get_set_of_ids(self, elements):
        """Converts a set/list/tuple of entities into a set of their ids"""
        
        new_set = set()
        for e in set(elements):
            new_set.add(self._reaction_system.get_entity_id(e))
        return new_set
    
    def add_transition(self, src, context_set, dst):
        if not type(context_set) is set and not type(context_set) is list:
            print("Contexts set must be of type set or list")
            
        if not self.is_valid_context(context_set):
            raise RuntimeError("one of the entities in the context set is unknown (undefined)!")
            
        if not self.is_state(src):
            raise RuntimeError("\"" + src + "\" is an unknown (undefined) state")

        if not self.is_state(dst):
            raise RuntimeError("\"" + dst + "\" is an unknown (undefined) state")

        new_context_set = set()
        for e in set(context_set):
            new_context_set.add(self._reaction_system.get_entity_id(e))
            
        self._prod_entities |= new_context_set
        
        self._transitions.append((self.get_state_id(src),new_context_set,self.get_state_id(dst)))

    def rsset2str(self, elements):
        """Converts the set of entities ids into the string with their names"""
        if len(elements) == 0:
            return "0"
        s = "{"
        for c in elements:
            s += " " + self._reaction_system.get_entity_name(c) 
        s += " }"
        return s
    
    def context2str(self, ctx):
        return self.rsset2str(ctx)
                
    def show_transitions(self):
        print(C_MARK_INFO + " Context automaton transitions:")
        for transition in self._transitions:
            str_transition = str(transition[0]) + " --( "
            str_transition += self.context2str(transition[1])
            str_transition += " )--> " + str(transition[2])
            print(" - " + str_transition)
    
    def show_states(self):
        init_state_name = self.get_init_state_name()
        print(C_MARK_INFO + " Context automaton states:")
        for state in self._states:
            print(" - " + state, end="")
            if state == init_state_name:
                print(" [init]")
            else:
                print()

    def show_header(self):
        if self.name:
            name_string = ": " + colour_str(C_BOLD, self.name)
            print(C_MARK_INFO + " Context automaton" + name_string)       

    def show_prod_entities(self):
        print(C_MARK_INFO + " Context automaton possible products:")
        for entity in self._prod_entities:
            print(" - " + self._reaction_system.get_entity_name(entity))
        
    def show(self):
        self.show_header()
        self.show_states()
        self.show_transitions()
        self.show_prod_entities()

