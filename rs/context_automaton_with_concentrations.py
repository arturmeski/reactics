from sys import exit
from colour import *

from rs.context_automaton import ContextAutomaton


class ContextAutomatonWithConcentrations(ContextAutomaton):

    def __init__(self, reaction_system):
        super(ContextAutomatonWithConcentrations,
              self).__init__(reaction_system)

    def is_valid_context(self, context):
        if set(
                [e for e, lvl in context]).issubset(
                self._reaction_system.background_set):
            return True
        else:
            return False

    def context2str(self, ctx):
        if len(ctx) == 0:
            return "0"
        s = "{"
        for ent, lvl in ctx:
            s += " " + str((self._reaction_system.get_entity_name(ent), lvl))
        s += " }"
        return s

    def add_transition(self, src, context_set, dst):
        if not type(context_set) is set and not type(context_set) is list:
            print("Contexts set must be of type set or list")

        if not self.is_valid_context(context_set):
            raise RuntimeError(
                "one of the entities in the context set is unknown (undefined)!")

        if not self.is_state(src):
            raise RuntimeError(
                "\"" + src + "\" is an unknown (undefined) state")

        if not self.is_state(dst):
            raise RuntimeError(
                "\"" + dst + "\" is an unknown (undefined) state")

        new_context_set = set()
        for ent, lvl in set(context_set):
            new_context_set.add(
                (self._reaction_system.get_entity_id(ent), lvl))

        self._transitions.append(
            (self.get_state_id(src),
             new_context_set, self.get_state_id(dst)))

    def get_automaton_with_flat_contexts(self, ordinary_reaction_system):

        ca = ContextAutomaton(ordinary_reaction_system)
        ca._states = self._states
        ca._init_state = self._init_state

        for src, ctx, dst in self._transitions:

            new_ctx = set()

            for ent, conc in ctx:
                for i in range(1, conc+1):
                    n = self._reaction_system.get_entity_name(
                        ent) + "#" + str(i)
                    ca._reaction_system.ensure_bg_set_entity(n)
                    new_ctx.add(n)

            ca.add_transition(
                ca.get_state_name(src),
                new_ctx, ca.get_state_name(dst))

        return ca

    def show(self):
        self.show_header()
        self.show_states()
        self.show_transitions()

# EOF
