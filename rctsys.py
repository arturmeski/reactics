#!/usr/bin/env python

"""
--- Reaction Systems Manipulation
"""

#
# TODO:
#
#  *  zamiast zbiorów - listy
#  *  index pobieramy za pomoca .index()
#  *  nie dopuszczamy modyfikacji listy stanow/background_set, itp.
#  *  uzywamy setterow i getterow
#

from sys import exit

class ContextAutomaton(object):
    
    def __init__(self, reaction_system):
        self.__states = []
        self.__transitions = []
        self.__init_state = None
        self.__reaction_system = reaction_system
    
    @property
    def states(self):
        return self.__states
    
    @property
    def transitions(self):
        return self.__transitions
    
    def add_state(self, name):
        if name not in self.__states:
            self.__states.append(name)
        else:
            print("\'%s\' already added. skipping..." % (name,))
            
    def add_init_state(self, name):
        self.add_state(name)
        self.__init_state = self.__states.index(name)

    def get_init_state_name(self):
        if self.__init_state == None:
            return None
        return self.__states[self.__init_state]

    def is_state(self, name):
        if name in self.__states:
            return True
        else:
            return False

    def get_state_id(self, name):
        try:
            return self.__states.index(name)
        except ValueError:
            print("Undefined context automaton state: " + repr(name))
            exit(1)

    def get_init_state_id(self):
        return self.__init_state
    
    def print_states(self):
         for state in self.__states:
            print(state)
            
    def is_valid_context(self, context):
        if set(context).issubset(self.__reaction_system.background_set):
            return True
        else:
            return False
        
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
            new_context_set.add(self.__reaction_system.get_entity_id(e))

        self.__transitions.append((self.get_state_id(src),new_context_set,self.get_state_id(dst)))

    def context2str(self, ctx):
        """Converts the set of entities ids into the string with their names"""
        if len(ctx) == 0:
            return "0"
        s = "{"
        for c in ctx:
            s += " " + self.__reaction_system.get_entity_name(c) 
        s += " }"
        return s
        
    def show_transitions(self):
        print("[*] Context automaton transitions:")
        for transition in self.__transitions:
            str_transition = str(transition[0]) + " --( "
            str_transition += self.context2str(transition[1])
            str_transition += " )--> " + str(transition[2])
            print("\t- " + str_transition)
    
    def show_states(self):
        init_state_name = self.get_init_state_name()
        print("[*] Context automaton states:")
        for state in self.__states:
            print("\t- " + state, end="")
            if state == init_state_name:
                print(" [init]")
            else:
                print()

    def show(self):
        self.show_states()
        self.show_transitions()


class ReactionSystem(object):

    def __init__(self):

        self.reactions = []
        self.background_set = []
        self.init_contexts = []
        self.context_entities = []

        self.reactions_by_agents = [] # each element is 'reactions_by_prod'

        self.reactions_by_prod = None

    def add_bg_set_entity(self, name):
        if not self.is_in_background_set(name):
            self.background_set.append(name)
        else:
            print("The entity", name, "is already on the list")
            raise

    def add_bg_set_entities(self, names):
        for name in names:
            self.add_bg_set_entity(name)

    def is_in_background_set(self, entity):
        """Checks if the given name is valid wrt the background set="""
        if entity in self.background_set:
            return True
        else:
            return False

    def get_entity_id(self, name):
        try:
            return self.background_set.index(name)
        except ValueError:
            print("Undefined background set entity: " + repr(name))
            exit(1)

    def get_state_ids(self, state):
        ids = []
        for entity in state:
            ids.append(self.get_entity_id(entity))

        return ids

    def get_entity_name(self, entity_id):
        """Returns the string corresponding to the entity"""
        return self.background_set[entity_id]


    def add_reaction(self, R, I, P):
        """Adds a reaction"""
        
        if R == [] or P == []:
            print("No reactants of products defined")
            raise

        reactants = []
        for entity in R:
            reactants.append(self.get_entity_id(entity))

        inhibitors = []
        for entity in I:
            inhibitors.append(self.get_entity_id(entity))

        products = []
        for entity in P:
            products.append(self.get_entity_id(entity))

        self.reactions.append((reactants, inhibitors, products))

    def add_initial_context_set(self, context_set):
        if context_set == []:
            print("Empty context set is not allowed")
            raise

        integers = []
        for entity in context_set:
            if not entity in self.background_set:
                print("The entity", entity, "is not in the background set")
                raise
            else:
                integers.append(self.get_entity_id(entity))

        self.init_contexts.append(integers)

    def set_context_entities(self, entities):

        for entity in entities:
            entity_id = self.get_entity_id(entity)
            self.context_entities.append(entity_id)

    def entities_names_set_to_str(self, entities):
        s = ""
        for entity in entities:
            s += entity + ", "
        s = s[:-2]
        return s

    def entities_ids_set_to_str(self, entities):
        s = ""
        for entity in entities:
            s += self.get_entity_name(entity) + ", "
        s = s[:-2]
        return s
        
    def state_to_str(self, state):
        return self.entities_ids_set_to_str(state)

    def show_reactions(self, soft=False):
        print("[*] Reactions:")
        if soft and len(self.reactions) > 50:
            print("\t -> there are more than 50 reactions (" + str(len(self.reactions)) + ")")
        else:
            for reaction in self.reactions:
                print("\t - ( R={" + self.state_to_str(reaction[0]) + "}, \tI={" + self.state_to_str(reaction[1]) + "}, \tP={" + self.state_to_str(reaction[2]) + "} )")

    def show_background_set(self):
        print("[*] Background set: {" + self.entities_names_set_to_str(self.background_set) + "}")

    def show_initial_contexts(self):
        if len(self.init_contexts) > 0:
            print("[*] Initial context sets:")
            for ctx in self.init_contexts:
                  print("\t - {" + self.entities_ids_set_to_str(ctx) + "}")

    def show_context_entities(self):
        if len(self.context_entities) > 0:
            print("[*] Context entities: " + self.entities_ids_set_to_str(self.context_entities))

    def show(self, soft=False):

        self.show_background_set()
        self.show_initial_contexts()
        self.show_reactions(soft)
        self.show_context_entities()
        
    def get_reactions_by_product(self):
        """Sorts reactions by their products and returns a dictionary of products"""

        if self.reactions_by_prod != None:
            return self.reactions_by_prod

        producible_entities = set()

        for reaction in self.reactions:
            producible_entities = producible_entities.union(set(reaction[2]))

        reactions_by_prod = {} 

        for prod_entity in producible_entities:
            reactions_by_prod[prod_entity] = []
            for reaction in self.reactions:
                if prod_entity in reaction[2]:
                    reactions_by_prod[prod_entity].append([reaction[0],reaction[1]])

        # save in cache
        self.reactions_by_prod = reactions_by_prod

        return reactions_by_prod

    def sanity_check(self):
        """Performs a sanity check on the defined reaction system"""

        if self.reactions == []:
            print("No reactions defined")
            exit(1)

        if self.background_set == []:
            print("Empty background set")
            exit(1)


class ReactionSystemWithConcentrations(ReactionSystem):

    def __init__(self):

        self.reactions = []
        self.background_set = []
        self.context_entities = []

        self.reactions_by_agents = [] # each element is 'reactions_by_prod'

        self.reactions_by_prod = None

    def get_entity_id(self, name):
        try:
            return self.background_set.index(name)
        except ValueError:
            print("Undefined background set entity: " + repr(name))
            exit(1)

    def get_state_ids(self, state):
        ids = []
        for entity in state:
            ids.append(self.get_entity_id(entity))
        return ids

    def is_valid_entity_with_concentration(self, e):
        """Sanity check for entities with concentration"""
        
        if type(e) is tuple:
            if len(e) == 2 and type(e[1]) is int:
                return True
                
        if type(e) is list:
            if len(e) == 2 and type(e[1]) is int:
                return True

        print("FATAL. Invalid entity+concentration:")
        print(e)
        exit(1)
        
        return False

    def add_reaction(self, R, I, P):
        """Adds a reaction"""
        
        if R == [] or P == []:
            print("No reactants of products defined")
            raise

        reactants = []
        for r in R:
            self.is_valid_entity_with_concentration(r)
            entity,level = r
            reactants.append((self.get_entity_id(entity),level))
            
        inhibitors = []
        for i in I:
            self.is_valid_entity_with_concentration(i)
            entity,level = i
            inhibitors.append((self.get_entity_id(entity),level))

        products = []
        for p in P:
            self.is_valid_entity_with_concentration(p)
            entity,level = p
            products.append((self.get_entity_id(entity),level))

        self.reactions.append((reactants, inhibitors, products))

    def set_context_entities(self, entities):
        raise NotImplementedError

    def entities_names_set_to_str(self, entities):
        s = ""
        for entity in entities:
            s += entity + ", "
        s = s[:-2]
        return s

    def entities_ids_set_to_str(self, entities):
        s = ""
        for entity in entities:
            s += self.get_entity_name(entity) + ", "
        s = s[:-2]
        return s

    def states_to_str(self, state):
        s = ""
        for entity,level in state:
            s += str((self.get_entity_name(entity),level)) + ", "
        s = s[:-2]
        return s        

    def show_background_set(self):
        print("[*] Background set: {" + self.entities_names_set_to_str(self.background_set) + "}")

    def show(self, soft=False):
        self.show_background_set()
        self.show_reactions(soft)
        
    def get_reactions_by_product(self):
        """Sorts reactions by their products and returns a dictionary of products"""

        if self.reactions_by_prod != None:
            return self.reactions_by_prod

        producible_entities = set()

        for reaction in self.reactions:
            producible_entities = producible_entities.union(set(reaction[2]))

        reactions_by_prod = {} 

        for prod_entity in producible_entities:
            reactions_by_prod[prod_entity] = []
            for reaction in self.reactions:
                if prod_entity in reaction[2]:
                    reactions_by_prod[prod_entity].append([reaction[0],reaction[1]])

        # save in cache
        self.reactions_by_prod = reactions_by_prod

        return reactions_by_prod


class ReactionSystemWithAutomaton(object):
    
    def __init__(self, reaction_system, context_automaton):
        self.rs = reaction_system
        self.ca = context_automaton

    def show(self, soft=False):
        self.rs.show(soft)
        self.ca.show()

