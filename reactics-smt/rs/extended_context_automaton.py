from sys import exit
from colour import *

from rs.context_automaton import ContextAutomaton


class ExtendedContextAutomaton(ContextAutomaton):
    """Extended Context Automaton

    Supports transitions with actions.

    Each transitions is additionally guarded with
    reactants and inhibitors.

    The provided context entities are the products
    of the reactions labelling the transition taken.
    """

    def __init__(self, reaction_system):
        super(ExtendedContextAutomaton, self).__init__(reaction_system)
        self._actions = []
        self._transitions_for_products = dict()
        self._actions_for_products = dict()

    @property
    def number_of_actions(self):
        return len(self._actions)

    @property
    def actions(self):
        return self._actions

    def has_action(self, action):
        """Checks if the automaton supports a given action"""

        return action in self._actions

    def get_transitions_producing_entity(self, entity):
        """Returns the transitions that produce a given entity"""

        if entity in self._transitions_for_products:
            return self._transitions_for_products[entity]
        else:
            return []

    def get_actions_producing_entity(self, entity):
        """Returns the actions that produce a given entity"""

        if entity in self._actions_for_products:
            return self._actions_for_products[entity]
        else:
            return set()

    def can_produce_entity(self, entity):
        """Check if the automaton can produce an entity"""

        if entity in self._actions_for_products:
            return True
        else:
            return False

    def add_transition(self, src, actions, ctx_reaction, dst):
        """Adds a transition

        src: is the source state name
        dst: is the destination state name
        actions: is the set of actions with which the transitions is synchronised
        ctx_reaction: is the context reaction associated with the transition
        """

        ctx_reactants, ctx_inhibitors, ctx_products = ctx_reaction

        if not type(ctx_products) is set and not type(ctx_products) is list:
            print("Contexts set (context products) must be of type set or list")

        if not self.is_valid_rs_set(ctx_reactants):
            raise RuntimeError(
                "one of the entities in the reactants set is unknown (undefined)!"
            )

        if not self.is_valid_rs_set(ctx_inhibitors):
            raise RuntimeError(
                "one of the entities in the inhibitors set is unknown (undefined)!"
            )

        if not self.is_valid_rs_set(ctx_products):
            raise RuntimeError(
                "one of the entities in the context set is unknown (undefined)!"
            )

        if not self.is_state(src):
            raise RuntimeError('"' + src + '" is an unknown (undefined) state')

        if not self.is_state(dst):
            raise RuntimeError('"' + dst + '" is an unknown (undefined) state')

        src_id = self.get_state_id(src)
        dst_id = self.get_state_id(dst)
        act_ids = self.get_set_of_action_ids(actions)
        r_ids = self.get_set_of_ids(ctx_reactants)
        i_ids = self.get_set_of_ids(ctx_inhibitors)
        p_ids = self.get_set_of_ids(ctx_products)

        new_transition = (src_id, act_ids, (r_ids, i_ids, p_ids), dst_id)

        for product_id in p_ids:
            self._transitions_for_products.setdefault(product_id, [])
            self._transitions_for_products[product_id].append(new_transition)
            self._actions_for_products.setdefault(product_id, set())
            self._actions_for_products[product_id] |= set(actions)

        self._prod_entities |= p_ids

        self._transitions.append(new_transition)

    def show_transitions(self):
        """Prints the set of registered transitions"""

        print(C_MARK_INFO + " Context automaton transitions:")
        for src_id, act_id, reaction, dst_id in self._transitions:
            str_transition = self.get_state_name(src_id) + " --( "
            str_transition += "<" + self.get_actions_str(act_id) + "> | "
            str_transition += (
                "( "
                + self.rsset2str(reaction[0])
                + ","
                + self.rsset2str(reaction[1])
                + ","
                + self.rsset2str(reaction[2])
                + " )"
            )
            str_transition += " )--> " + self.get_state_name(dst_id)
            print(" - " + str_transition)

    def add_action(self, action_name):
        """Registers an action"""

        if action_name not in self._actions:
            self._actions.append(action_name)
        else:
            print("'%s' already added. skipping..." % (action_name,))

    def get_action_id(self, action_name):
        """For an action name returns its id"""

        try:
            return self._actions.index(action_name)
        except ValueError:
            print_error("Undefined context automaton action: " + repr(action_name))
            exit(1)

    def get_action_name(self, action_id):
        return self._actions[action_id]

    def get_set_of_action_ids(self, actions):
        """Converts a set of actions into the set of their ids"""

        act_ids = set()
        for act in actions:
            act_ids.add(self.get_action_id(act))
        return act_ids

    def get_actions_str(self, actions):
        """Returns the string for the set of action ids given by actions"""

        s = ""
        for act in actions:
            s += self.get_action_name(act) + ", "
        s = s[:-2]
        return s

    def show_actions(self):
        """Prints all the actions"""

        print(C_MARK_INFO + " Context automaton actions:")
        for act in self._actions:
            print(" - " + act + " (id=" + str(self.get_action_id(act)) + ")")

    def show(self):
        super(ExtendedContextAutomaton, self).show()
        self.show_actions()


# EOF
