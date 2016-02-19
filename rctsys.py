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
        self._states = []
        self._transitions = []
        self._init_state = None
        self._reaction_system = reaction_system
    
    @property
    def states(self):
        return self._states
    
    @property
    def transitions(self):
        return self._transitions
    
    def add_state(self, name):
        if name not in self._states:
            self._states.append(name)
        else:
            print("\'%s\' already added. skipping..." % (name,))
            
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
            print("Undefined context automaton state: " + repr(name))
            exit(1)

    def get_init_state_id(self):
        return self._init_state
    
    def print_states(self):
         for state in self._states:
            print(state)
            
    def is_valid_context(self, context):
        if set(context).issubset(self._reaction_system.background_set):
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
            new_context_set.add(self._reaction_system.get_entity_id(e))
        
        self._transitions.append((self.get_state_id(src),new_context_set,self.get_state_id(dst)))

    def context2str(self, ctx):
        """Converts the set of entities ids into the string with their names"""
        if len(ctx) == 0:
            return "0"
        s = "{"
        for c in ctx:
            s += " " + self._reaction_system.get_entity_name(c) 
        s += " }"
        return s
        
    def show_transitions(self):
        print("[*] Context automaton transitions:")
        for transition in self._transitions:
            str_transition = str(transition[0]) + " --( "
            str_transition += self.context2str(transition[1])
            str_transition += " )--> " + str(transition[2])
            print("\t- " + str_transition)
    
    def show_states(self):
        init_state_name = self.get_init_state_name()
        print("[*] Context automaton states:")
        for state in self._states:
            print("\t- " + state, end="")
            if state == init_state_name:
                print(" [init]")
            else:
                print()

    def show(self):
        self.show_states()
        self.show_transitions()


class ContextAutomatonWithConcentrations(ContextAutomaton):

    def __init__(self, reaction_system):
        self._states = []
        self._transitions = []
        self._init_state = None
        self._reaction_system = reaction_system
    
    def is_valid_context(self, context):
        if set([e for e,lvl in context]).issubset(self._reaction_system.background_set):
            return True
        else:
            return False
            
    def context2str(self, ctx):
        if len(ctx) == 0:
            return "0"
        s = "{"
        for ent,lvl in ctx:
            s += " " + str((self._reaction_system.get_entity_name(ent),lvl)) 
        s += " }"
        return s
        
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
        for ent,lvl in set(context_set):
            new_context_set.add((self._reaction_system.get_entity_id(ent),lvl))
        
        self._transitions.append((self.get_state_id(src),new_context_set,self.get_state_id(dst)))

class ReactionSystem(object):

    def __init__(self):

        self.reactions = []
        self.background_set = []

        #self.reactions_by_agents = [] # each element is 'reactions_by_prod'
        self.reactions_by_prod = None

        ## legacy:
        self.init_contexts = []
        self.context_entities = []

    def add_bg_set_entity(self, name):
        if not self.is_in_background_set(name):
            self.background_set.append(name)
        else:
            raise RuntimeError("The entity " + name + " is already on the list")
    
    def ensure_bg_set_entity(self, name):
        if not self.is_in_background_set(name):
            self.background_set.append(name)

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
        self.reactions_by_prod = None

        self.max_concentration = 0

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

    def get_state_ids(self, state):
        """Returns entities of the given state without levels"""
        return [e for e,c in state]

    def has_non_zero_concentration(self, elem):
        if elem[1] < 1:
            raise RuntimeError("Unexpected concentration level in state: " + str(elem))

    def add_reaction(self, R, I, P):
        """Adds a reaction"""
        
        if R == [] or P == []:
            print("No reactants of products defined")
            raise

        reactants = []
        for r in R:
            self.is_valid_entity_with_concentration(r)
            self.has_non_zero_concentration(r)
            entity,level = r
            reactants.append((self.get_entity_id(entity),level))
            if self.max_concentration < level:
                self.max_concentration = level
            
        inhibitors = []
        for i in I:
            self.is_valid_entity_with_concentration(i)
            self.has_non_zero_concentration(i)
            entity,level = i
            inhibitors.append((self.get_entity_id(entity),level))
            if self.max_concentration < level:
                self.max_concentration = level

        products = []
        for p in P:
            self.is_valid_entity_with_concentration(p)
            self.has_non_zero_concentration(p)
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

    def state_to_str(self, state):
        s = ""
        for ent,level in state:
            s += str((self.get_entity_name(ent),level)) + ", "
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
            product_entities = [e for e,c in reaction[2]]
            producible_entities = producible_entities.union(set(product_entities))

        reactions_by_prod = {}

        for p_e in producible_entities:
            reactions_by_prod[p_e] = []
            for r in self.reactions:
                product_entities = [e for e,c in r[2]]
                if p_e in product_entities:
                    reactants = r[0]
                    inhibitors = r[1]
                    products = [(e,c) for e,c in r[2] if e == p_e]
                    reactions_by_prod[p_e].append((reactants, inhibitors, products))

        # save in cache
        self.reactions_by_prod = reactions_by_prod

        return reactions_by_prod

    def get_reaction_system(self):
        
        rs = ReactionSystem()
                
        for reactants,inhibitors,products in self.reactions:

            new_reactants = []
            new_inhibitors = []
            new_products = []

            for ent,conc in reactants:
                n = self.get_entity_name(ent) + "_" + str(conc)
                rs.ensure_bg_set_entity(n)
                new_reactants.append(n)
                
            for ent,conc in inhibitors:
                n = self.get_entity_name(ent) + "_" + str(conc)
                rs.ensure_bg_set_entity(n)
                new_inhibitors.append(n)

            for ent,conc in products:
                for i in range(1,conc+1):
                    n = self.get_entity_name(ent) + "_" + str(i)
                    rs.ensure_bg_set_entity(n)
                    new_products.append(n)
                            
            rs.add_reaction(new_reactants,new_inhibitors,new_products)
        
        return rs
    

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

# class ReactionSystemWithConcentrationWithAutomaton(ReactionSystemWithAutomaton):
#
#     def __init__(self, reaction_system, context_automaton):
#         self.rs = reaction_system
#         self.ca = context_automaton
#
#     def show(self, soft=False):
#         self.rs.show(soft)
#         self.ca.show()
