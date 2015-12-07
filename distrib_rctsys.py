#!/usr/bin/env python

"""
--- Distributed Reaction Systems Manipulation
"""

from sys import exit

class DistributedReactionSystem(object):

    def __init__(self):

        self.__reactions = []
        self.__background_set = []
        self.__reactions_by_prod = []
        self.__states = []
        self.__transitions = []
        self.__init_state = None

        self.__context_sets_size = None

    @property
    def background_set(self):
        return self.__background_set
    
    @property
    def set_of_background_ids(self):
        return set(range(len(self.__background_set)))

    @property
    def components_count(self):
        return len(self.__reactions)

    def add_bg_set_entity(self, name):
        if not self.is_in_background_set(name):
            self.__background_set.append(name)
        else:
            print("The entity \"" + str(name) + "\" is already on the list")
            exit(1)

    def add_bg_set_entities(self, names):
        for name in names:
            self.add_bg_set_entity(name)

    def is_in_background_set(self, entity):
        """Checks if the given name is valid wrt the background set="""
        if entity in self.__background_set:
            return True
        else:
            return False

    def get_entity_id(self, name):
        try:
            return self.__background_set.index(name)
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
        return self.__background_set[entity_id]

    def ensure_reactions(self, k):
        while len(self.__reactions) <= k:
            self.__reactions.append([])

    def add_reaction(self, k, R, I, P):
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
        
        self.ensure_reactions(k)
        self.__reactions[k].append((reactants, inhibitors, products))
        
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

    def show_reactions(self):
        print("[*] Reactions:")
        for i in range(len(self.__reactions)):
            local_reactions = self.__reactions[i]
            print("    agent = " + str(i))
            for rcts,inhib,prods in local_reactions:
                print("\t - ( R={" + self.entities_ids_set_to_str(rcts) + "}, \tI={" + self.entities_ids_set_to_str(inhib) + "}, \tP={" + self.entities_ids_set_to_str(prods) + "} )")

    def show_background_set(self):
        print("[*] Background set: {" + self.entities_names_set_to_str(self.__background_set) + "}")

    def show(self):
        self.show_background_set()
        self.show_reactions()
        self.show_states()
        self.show_transitions()
        print()
        
    def reactions_by_product_are_cached(self, component_id):
        if len(self.__reactions_by_prod) > component_id:
            if self.__reactions_by_prod[component_id] != None:
                return True
        return False
        
    def get_reactions_by_product(self, component_id):
        """Sorts reactions for the component given by component_id by their products and returns a dictionary of products"""
        
        if self.reactions_by_product_are_cached(component_id):
            return self.__reactions_by_prod[component_id]

        producible_entities = set()

        for reactants,inhibitors,products in self.__reactions[component_id]:
            producible_entities = producible_entities.union(set(products))

        reactions_by_prod = dict()

        for prod_entity in producible_entities:
            reactions_by_prod[prod_entity] = []
            for reactants,inhibitors,products in self.__reactions[component_id]:
                if prod_entity in products:
                    reactions_by_prod[prod_entity].append([reactants,inhibitors])

        # save in cache
        while len(self.__reactions_by_prod) <= component_id: # ensure that the size of cache is right
            self.__reactions_by_prod.append(None)
        self.__reactions_by_prod[component_id] = reactions_by_prod

        return reactions_by_prod

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
    
    def is_valid_context_sets(self, context_sets):
        for c in context_sets:
            if not self.is_valid_context(c):
                return False
        return True
    
    def is_valid_context(self, context):
        if set(context).issubset(self.__background_set):
            return True
        else:
            return False
        
    def add_transition(self, src, label, dst):
        recipients = label[0]
        context_sets = label[1]
        if not type(context_sets) is list:
            print("Context sets must be of type list")
            exit(1)
        for s in context_sets:
            if not type(s) is set and not type(s) is list:
                print("Each context set must be of type set or list")
                exit(1)
                
        if self.__context_sets_size == None:
            self.__context_sets_size = len(context_sets)
        else:
            if len(context_sets) != self.__context_sets_size:
                print("Inconsistent size of the context sets: " + str(len(context_sets)) + " != " + str(self.__context_sets_size))
                exit(1)
                
        if not self.is_valid_context_sets(context_sets):
            raise RuntimeError("one of the entities in the context set is unknown (undefined)!")
            
        if not self.is_state(src):
            raise RuntimeError("\"" + src + "\" is an unknown (undefined) state")

        if not self.is_state(dst):
            raise RuntimeError("\"" + dst + "\" is an unknown (undefined) state")

        new_context_sets = []
        for c in context_sets:
            new_c_set = set()
            for e in set(c):
                new_c_set.add(self.get_entity_id(e))
            new_context_sets.append(new_c_set)

        recipients = set(recipients)

        self.__transitions.append((self.get_state_id(src),(recipients,new_context_sets),self.get_state_id(dst)))

    def context2str(self, context_sets):
        """Converts the set of entities ids into the string with their names"""
        s = "["
        for ctx in context_sets:
            if len(ctx) == 0:
                s += " 0"
            else:
                s += " {"
                for c in ctx:
                    s += " " + self.get_entity_name(c) 
                s += " }"
        s += " ]"
        return s
        
    def show_transitions(self):
        print("[*] Context automaton transitions:")
        for transition in self.__transitions:
            str_transition = str(transition[0]) + " --( "
            str_transition += str(list(transition[1][0])) + "<=" + self.context2str(transition[1][1])
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

    def sanity_check(self):
        """Performs a sanity check of the defined distributed reaction system"""

        print("[i] Performing sanity check of the DRS")

        if self.__reactions == []:
            print("No reactions defined")
            exit(1)

        if self.__background_set == []:
            print("Empty background set")
            exit(1)

        if self.__init_state == None:
            print("Initial state not specified")
            exit(1)

        if self.__context_sets_size != len(self.__reactions):
            print("Inconsistent sizes of the context sets with respect to the number of components/agents/processes: " + str(self.__context_sets_size) + " != " + str(len(self.__reactions)))
            exit(1)

