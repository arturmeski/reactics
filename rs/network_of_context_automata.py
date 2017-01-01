from sys import exit
from colour import *

class NetworkOfContextAutomata(object):
    
    def __init__(self, reaction_system, context_automata):
        self.automata = []
        self._reaction_system = reaction_system
        self._actions = set()
        self._prod_entities = set()
        self._automata_for_actions = dict()
        self._actions_for_products = dict()

        if len(context_automata) < 1:
            print("Context automata network must contain at least one automaton!")
            exit(1)
            
        for automaton in context_automata:
            self.add(automaton)

        self.sanity_check()

    @property
    def number_of_automata(self):
        return len(self.automata)

    @property
    def reaction_system(self):
        return self._reaction_system

    @property
    def prod_entities(self):
        """Returns the set of entities that can potentially be produced by the automata in the network"""
        return self._prod_entities

    @property
    def automata_ids(self):
        return set(range(len(self.automata)))

    def sanity_check(self):
        """Performs a sanity check of the network of automata"""
        
        for automaton in self.automata:
            if automaton.reaction_system != self._reaction_system:
                print_error("Mismatching reaction system used in \"" + str(automaton.name) + "\"!!!")
                exit(1)

    def show_prod_entities(self):
        print(C_MARK_INFO + " Possible context-products for the network of automata:")
        for entity in self.prod_entities:
            print(" - " + self._reaction_system.get_entity_name(entity))

    def show_actions(self):
        print(C_MARK_INFO + " Actions of the network:")
        for action in self._actions:
            print(" - " + action)

    def register_action(self, action, aut):
        """Associates an action with an automaton"""
        
        self._automata_for_actions.setdefault(action, set())
        aut_index = self.automata.index(aut)
        self._automata_for_actions[action].add(aut_index)
        
    def get_actions_producing_entity(self, entity):
        """Returns the set of actions producing an entity"""
        
        if entity in self._actions_for_products:
            return self._actions_for_products[entity]
        else:
            return set()
            
    def get_automata_with_action(self, action):
        """Returns the set of automata that support an action"""
        
        if action in self._automata_for_actions:
            return self._automata_for_actions[action]
        else:
            return set()

    def add(self, aut):
        """Adds an automaton to the network"""
        
        self.automata.append(aut)
        self._prod_entities |= aut.prod_entities
        self._actions |= set(aut.actions)
        
        for action in aut.actions:
            self.register_action(action, aut)

        for entity in aut.prod_entities:
            self._actions_for_products.setdefault(entity, set())
            self._actions_for_products[entity] |= aut.get_actions_producing_entity(entity)

    def show(self):
        print()
        print(C_MARK_INFO + " NETWORK OF CONTEXT AUTOMATA")
        for ca in self.automata:
            print()
            ca.show()
        print()
        self.show_prod_entities()
        self.show_actions()
        