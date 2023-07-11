from sys import exit
from colour import *


class ReactionSystem(object):
    def __init__(self):
        self.reactions = []
        self.background_set = []

        # self.reactions_by_agents = [] # each element is 'reactions_by_prod'
        self.reactions_by_prod = None

        # legacy:
        self.init_contexts = []
        self.context_entities = []

    @property
    def background_set_size(self):
        return len(self.background_set)

    @property
    def set_of_bgset_ids(self):
        return set(range(self.background_set_size))

    @property
    def ordered_list_of_bgset_ids(self):
        return list(range(self.background_set_size))

    def assume_not_in_bgset(self, name):
        if self.is_in_background_set(name):
            raise RuntimeError("The entity " + name + " is already on the list")

    def add_bg_set_entity(self, name):
        self.assume_not_in_bgset(name)
        self.background_set.append(name)

    def ensure_bg_set_entity(self, name):
        if not self.is_in_background_set(name):
            self.background_set.append(name)

    def add_bg_set_entities(self, elements):
        for e in elements:
            self.add_bg_set_entity(e)

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
            raise RuntimeError("No reactants or products defined")

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
        print(C_MARK_INFO + " Reactions:")
        if soft and len(self.reactions) > 50:
            print(
                " -> there are more than 50 reactions ("
                + str(len(self.reactions))
                + ")"
            )
        else:
            print(
                " " * 4
                + "{0: ^35}{1: ^25}{2: ^15}".format(
                    "reactants", " inhibitors", " products"
                )
            )
            for reaction in self.reactions:
                # print("\t( R={" + self.state_to_str(reaction[0]) + "}, I={" + self.state_to_str(reaction[1]) + "}, P={" + self.state_to_str(reaction[2]) + "} )")
                print(
                    " "
                    + "- {0: ^35}{1: ^25}{2: ^15}".format(
                        "{ " + self.state_to_str(reaction[0]) + " }",
                        " { " + self.state_to_str(reaction[1]) + " }",
                        " { " + self.state_to_str(reaction[2]) + " }",
                    )
                )

    def show_background_set(self):
        print(
            C_MARK_INFO
            + " Background set: {"
            + self.entities_names_set_to_str(self.background_set)
            + "}"
        )

    def show_initial_contexts(self):
        if len(self.init_contexts) > 0:
            print(C_MARK_INFO + " Initial context sets:")
            for ctx in self.init_contexts:
                print(" - {" + self.entities_ids_set_to_str(ctx) + "}")

    def show_context_entities(self):
        if len(self.context_entities) > 0:
            print(
                C_MARK_INFO
                + " Context entities: "
                + self.entities_ids_set_to_str(self.context_entities)
            )

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
                    reactions_by_prod[prod_entity].append([reaction[0], reaction[1]])

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


# EOF
