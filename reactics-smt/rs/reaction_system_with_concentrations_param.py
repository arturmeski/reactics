from sys import exit
from colour import *

from rs.reaction_system import ReactionSystem


class ParameterObj(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "@{0}".format(self.name)


def is_param(some_object):
    if isinstance(some_object, ParameterObj):
        return True
    else:
        return False


class ReactionSystemWithConcentrationsParam(ReactionSystem):
    def __init__(self):
        self.reactions = []
        self.parameters = dict()
        self.meta_reactions = dict()
        self.permanent_entities = dict()
        self.background_set = []
        self.context_entities = []  # legacy. to be removed
        self.reactions_by_prod = None
        self.max_concentration = 1
        self.max_conc_per_ent = dict()

    def add_bg_set_entity(self, e):
        name = ""
        def_max_conc = -1
        if type(e) is tuple and len(e) == 2:
            name, def_max_conc = e
        elif type(e) is str:
            name = e
            print("\nWARNING: no maximal concentration level specified for:", e, "\n")
        else:
            raise RuntimeError("Bad entity type when adding background set element")

        self.assume_not_in_bgset(name)
        self.background_set.append(name)

        if def_max_conc != -1:
            ent_id = self.get_entity_id(name)
            self.max_conc_per_ent.setdefault(ent_id, 0)
            if self.max_conc_per_ent[ent_id] < def_max_conc:
                self.max_conc_per_ent[ent_id] = def_max_conc
            if self.max_concentration < def_max_conc:
                self.max_concentration = def_max_conc

    def get_param(self, name):
        if self.has_param(name):
            return self.parameters[name]
        else:
            param = ParameterObj(name)
            self.add_param(param)
            return param

    def has_param(self, name):
        return name in self.parameters

    def add_param(self, param):
        if param in self.parameters:
            raise RuntimeError("Parameter {:s} already exists".format(param))
        param_key = param.name
        self.parameters[param_key] = param
        self.parameters[param_key].idx = len(self.parameters)

    def get_max_concentration_level(self, e):
        if e in self.max_conc_per_ent:
            return self.max_conc_per_ent[e]
        else:
            return self.max_concentration

    def is_valid_entity_with_concentration(self, e):
        """Sanity check for entities with concentration"""

        if type(e) is tuple:
            if len(e) == 2 and type(e[1]) is int:
                return True

        if type(e) is list:
            if len(e) == 2 and type(e[1]) is int:
                return True

        print("FATAL. Invalid entity+concentration: {:s}".format(e))
        exit(1)

        return False

    def is_valid_concentration_for_entity(self, entity, level):
        """Checks the concentration level for entity"""
        e = self.get_entity_id(entity)
        try:
            max_conc = self.max_conc_per_ent[e]
        except KeyError as _:
            return True

        if level > max_conc:
            return False

        return True

    def terminate_on_invalid_concentration(self, entity, level):
        if not self.is_valid_concentration_for_entity(entity, level):
            print(
                "FATAL. Invalid entity concentration: {:s}={:d}".format(entity, level)
            )
            exit(1)

    def get_state_ids(self, state):
        """Returns entities of the given state without levels"""
        return [self.get_entity_id(e) for e in state]

    def has_non_zero_concentration(self, elem):
        if elem[1] < 1:
            raise RuntimeError("Unexpected concentration level in state: " + str(elem))

    def process_rip(self, R, I, P, ignore_empty_R=False):
        """Chcecks concentration levels and converts entities names into their ids"""

        if R == [] and not ignore_empty_R:
            raise RuntimeError("No reactants defined")

        #
        # REACTANTS
        #
        reactants = []
        if isinstance(R, ParameterObj):
            reactants = R
        else:
            for r in R:
                self.is_valid_entity_with_concentration(r)
                self.has_non_zero_concentration(r)
                entity, level = r
                self.terminate_on_invalid_concentration(entity, level)
                reactants.append((self.get_entity_id(entity), level))
                if self.max_concentration < level:
                    self.max_concentration = level

        #
        # INHIBITORS
        #
        inhibitors = []
        if isinstance(I, ParameterObj):
            inhibitors = I
        else:
            for i in I:
                self.is_valid_entity_with_concentration(i)
                self.has_non_zero_concentration(i)
                entity, level = i
                self.terminate_on_invalid_concentration(entity, level)
                inhibitors.append((self.get_entity_id(entity), level))
                if self.max_concentration < level:
                    self.max_concentration = level

        #
        # PRODUCTS
        #
        products = []
        if isinstance(P, ParameterObj):
            products = P
        else:
            for p in P:
                self.is_valid_entity_with_concentration(p)
                self.has_non_zero_concentration(p)
                entity, level = p
                self.terminate_on_invalid_concentration(entity, level)
                products.append((self.get_entity_id(entity), level))

        return reactants, inhibitors, products

    def is_parametric_reaction(self, reaction):
        result = any([isinstance(r_set, ParameterObj) for r_set in reaction])
        return result

    def add_reaction(self, R, I, P):
        """Adds a reaction

        R, I, and P are sets of entities (not their IDs)
        """

        if P == []:
            raise RuntimeError("No products defined")
        reaction = self.process_rip(R, I, P)

        self.reactions.append(reaction)

    def add_reaction_without_reactants(self, R, I, P):
        """Adds a reaction"""

        if P == []:
            raise RuntimeError("No products defined")
        reaction = self.process_rip(R, I, P, ignore_empty_R=True)
        self.reactions.append(reaction)

    def add_reaction_inc(self, incr_entity, incrementer, R, I):
        """Adds a macro/meta reaction for increasing the value of incr_entity"""

        reactants, inhibitors, products = self.process_rip(
            R, I, [], ignore_empty_R=True
        )
        incr_entity_id = self.get_entity_id(incr_entity)
        self.meta_reactions.setdefault(incr_entity_id, [])
        self.meta_reactions[incr_entity_id].append(
            ("inc", self.get_entity_id(incrementer), reactants, inhibitors)
        )

    def add_reaction_dec(self, decr_entity, decrementer, R, I):
        """Adds a macro/meta reaction for decreasing the value of incr_entity"""

        reactants, inhibitors, products = self.process_rip(
            R, I, [], ignore_empty_R=True
        )
        decr_entity_id = self.get_entity_id(decr_entity)
        self.meta_reactions.setdefault(decr_entity_id, [])
        self.meta_reactions[decr_entity_id].append(
            ("dec", self.get_entity_id(decrementer), reactants, inhibitors)
        )

    def add_permanency(self, ent, I):
        """Sets entity to be permanent unless it is inhibited"""

        ent_id = self.get_entity_id(ent)

        if ent_id in self.permanent_entities:
            raise RuntimeError("Permanency for {0} already defined.".format(ent))

        inhibitors = self.process_rip([], I, [], ignore_empty_R=True)[1]
        self.permanent_entities[ent_id] = inhibitors

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
        """
        If state is a parameter, we return
        the string representation of the whole state
        which should be the name of the parameter
        """
        if isinstance(state, ParameterObj):
            return str(state)
        else:
            s = ""
            for ent, level in state:
                s += self.get_entity_name(ent) + "=" + str(level) + ", "
            s = s[:-2]
        return s

    def show_background_set(self):
        print(
            C_MARK_INFO
            + " Background set: {"
            + self.entities_names_set_to_str(self.background_set)
            + "}"
        )

    def show_meta_reactions(self):
        print(C_MARK_INFO + " Meta reactions:")
        for param_ent, reactions in self.meta_reactions.items():
            for r_type, command, reactants, inhibitors in reactions:
                if r_type == "inc" or r_type == "dec":
                    print(
                        " - [ Type="
                        + repr(r_type)
                        + " Operand=( "
                        + self.get_entity_name(param_ent)
                        + " ) Command=( "
                        + self.get_entity_name(command)
                        + " ) ] -- ( R={"
                        + self.state_to_str(reactants)
                        + "}, I={"
                        + self.state_to_str(inhibitors)
                        + "} )"
                    )
                else:
                    raise RuntimeError("Unknown meta-reaction type: " + repr(r_type))

    def show_max_concentrations(self):
        print(C_MARK_INFO + " Maximal allowed concentration levels:")
        for e, max_conc in self.max_conc_per_ent.items():
            print(" - {0:^20} = {1:<6}".format(self.get_entity_name(e), max_conc))

    def show_permanent_entities(self):
        print(C_MARK_INFO + " Permanent entities:")
        for e, inhibitors in self.permanent_entities.items():
            print(
                " - {0:^20}{1:<6}".format(
                    self.get_entity_name(e) + ": ",
                    "I={" + self.state_to_str(inhibitors) + "}",
                )
            )

    def show(self, soft=False):
        self.show_background_set()
        self.show_reactions(soft)
        # self.show_param_reactions(soft)
        self.show_permanent_entities()
        self.show_meta_reactions()
        self.show_max_concentrations()

    def get_producible_entities(self):
        """
        Returns the set of entities that appear as products of
        reactions.
        """

        producible_entities = set()

        for reaction in self.reactions:
            product_entities = [e for e, c in reaction[2] if c > 0]
            producible_entities = producible_entities.union(set(product_entities))

        return producible_entities

    def get_reaction_system(self):
        """
        Translates RSC into RS
        """

        rs = ReactionSystem()

        for reactants, inhibitors, products in self.reactions:
            new_reactants = []
            new_inhibitors = []
            new_products = []

            for ent, conc in reactants:
                n = self.get_entity_name(ent) + "#" + str(conc)
                rs.ensure_bg_set_entity(n)
                new_reactants.append(n)

            for ent, conc in inhibitors:
                n = self.get_entity_name(ent) + "#" + str(conc)
                rs.ensure_bg_set_entity(n)
                new_inhibitors.append(n)

            for ent, conc in products:
                for i in range(1, conc + 1):
                    n = self.get_entity_name(ent) + "#" + str(i)
                    rs.ensure_bg_set_entity(n)
                    new_products.append(n)

            rs.add_reaction(new_reactants, new_inhibitors, new_products)

        for param_ent, reactions in self.meta_reactions.items():
            for r_type, command, reactants, inhibitors in reactions:
                param_ent_name = self.get_entity_name(param_ent)

                new_reactants = []
                new_inhibitors = []

                for ent, conc in reactants:
                    n = self.get_entity_name(ent) + "#" + str(conc)
                    rs.ensure_bg_set_entity(n)
                    new_reactants.append(n)

                for ent, conc in inhibitors:
                    n = self.get_entity_name(ent) + "#" + str(conc)
                    rs.ensure_bg_set_entity(n)
                    new_inhibitors.append(n)

                max_cmd_c = self.max_concentration
                if command in self.max_conc_per_ent:
                    max_cmd_c = self.max_conc_per_ent[command]
                else:
                    print(
                        "WARNING:\n\tThere is no maximal concentration level defined for "
                        + self.get_entity_name(command)
                    )
                    print("\tThis is a very bad idea -- expect degraded performance\n")

                for l in range(1, max_cmd_c + 1):
                    cmd_ent = self.get_entity_name(command) + "#" + str(l)
                    rs.ensure_bg_set_entity(cmd_ent)

                    if r_type == "inc":
                        # pre_conc  -- predecessor concentration
                        # succ_conc -- successor concentration concentration

                        for i in range(1, self.max_concentration):
                            pre_conc = param_ent_name + "#" + str(i)
                            rs.ensure_bg_set_entity(pre_conc)
                            new_products = []
                            succ_value = i + l
                            for j in range(1, succ_value + 1):
                                if j > self.max_concentration:
                                    break
                                new_p = param_ent_name + "#" + str(j)
                                rs.ensure_bg_set_entity(new_p)
                                new_products.append(new_p)
                            if new_products != []:
                                rs.add_reaction(
                                    set(new_reactants + [pre_conc, cmd_ent]),
                                    set(new_inhibitors),
                                    set(new_products),
                                )

                    elif r_type == "dec":
                        for i in range(1, self.max_concentration + 1):
                            pre_conc = param_ent_name + "#" + str(i)
                            rs.ensure_bg_set_entity(pre_conc)
                            new_products = []
                            succ_value = i - l
                            for j in range(1, succ_value + 1):
                                if j > self.max_concentration:
                                    break
                                new_p = param_ent_name + "#" + str(j)
                                rs.ensure_bg_set_entity(new_p)
                                new_products.append(new_p)
                            if new_products != []:
                                rs.add_reaction(
                                    set(new_reactants + [pre_conc, cmd_ent]),
                                    set(new_inhibitors),
                                    set(new_products),
                                )

                    else:
                        raise RuntimeError(
                            "Unknown meta-reaction type: " + repr(r_type)
                        )

        for ent, inhibitors in self.permanent_entities.items():
            max_c = self.max_concentration
            if ent in self.max_conc_per_ent:
                max_c = self.max_conc_per_ent[ent]
            else:
                print(
                    "WARNING:\n\tThere is no maximal concentration level defined for "
                    + self.get_entity_name(ent)
                )
                print("\tThis is a very bad idea -- expect degraded performance\n")

            def e_value(i):
                return self.get_entity_name(ent) + "#" + str(i)

            for value in range(1, max_c + 1):
                new_reactants = []
                new_inhibitors = []
                new_products = []

                new_reactants = [e_value(value)]

                for e_inh, conc in inhibitors:
                    n = self.get_entity_name(e_inh) + "#" + str(conc)
                    rs.ensure_bg_set_entity(n)
                    new_inhibitors.append(n)

                for i in range(1, value + 1):
                    new_products.append(e_value(i))

                rs.add_reaction(new_reactants, new_inhibitors, new_products)

        return rs


# EOF
