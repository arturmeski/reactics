#!/usr/bin/env python

import sys
import itertools


class SingleReaction:
    def __init__(self, reactants=None, inhibitors=None, products=None):
        self.reactants = set(reactants) if reactants is not None else set()
        self.inhibitors = set(inhibitors) if inhibitors is not None else set()
        self.products = set(products) if products is not None else set()

    def get_reactants(self):
        return "{" + ", ".join(self.reactants) + "}"

    def get_inhibitors(self):
        return "{" + ", ".join(self.inhibitors) + "}"

    def get_products(self):
        return "{" + ", ".join(self.products) + "}"

    def __str__(self):
        return (
            "{"
            + f"{self.get_reactants()}, {self.get_inhibitors()} -> {self.get_products()}"
            + "};"
        )


class Reactions:
    def __init__(self):
        self.reactions = []

    def add(self, reaction):
        self.reactions.append(reaction)

    def __str__(self):
        ret = ""
        for r in self.reactions:
            ret += f"{r}\n"
        return ret


class Transition:
    def __init__(self, src, dst, guard, context):
        self.src = src
        self.dst = dst
        self.guard = guard
        self.context = context

    def get_context_str(self):
        r = []
        for proc, entities in self.context:
            ent_str = ",".join(entities)
            r.append(f"{proc}={{{ent_str}}}")

        r = " ".join(r)
        return "{ " + r + " }"

    def __str__(self):
        return f"{self.get_context_str()}: {self.src} -> {self.dst} : {self.guard};"


class Automaton:
    def __init__(self):
        self.transitions = []
        self.states = []
        self.init_state = None

    def add_transition(self, transition):
        self.transitions.append(transition)

    def add_state(self, state):
        if state not in self.states:
            self.states.append(state)

    def set_init_state(self, state):
        assert state in self.states, f"{state} not in states"
        self.init_state = state

    def __str__(self):
        r = "context-automaton {\n"
        r += "\tstates { " + ", ".join(self.states) + " };\n"
        r += f"\tinit-state {{ {self.init_state} }};\n"
        r += "\ttransitions {\n"
        for tr in self.transitions:
            r += "\t\t" + str(tr) + "\n"
        r += "\t};\n"
        r += "};\n"
        return r


class DRSGenerator:
    def __init__(self, x, y, z, n):
        assert y >= z
        assert x >= 2 and y >= 2 and z >= 2
        self.x = x
        self.y = y
        self.z = z
        self.n = n
        self.reactions = {}

        self.automaton = Automaton()

        self.generate()

    def generate_agent_zero(self):
        rcts = Reactions()
        for i in range(1, self.y + 1):
            rcts.add(SingleReaction(["RTK"], ["h"], [f"RTK{i}"]))
            for j in range(1, self.x + 1):
                rcts.add(SingleReaction([f"EN:{j}_{i}"], ["h"], [f"ENi:{self.x}_{i}"]))
        return rcts

    def generate_reactions_for_component(self, i):
        self.reactions.setdefault(i, Reactions())
        rcts = self.reactions[i]
        rcts.add(SingleReaction(["GF"], ["h"], ["GF"]))
        rcts.add(SingleReaction(["GF"], ["h", f"RTK{i}"], ["RTK"]))
        rcts.add(SingleReaction(["RTK"], [f"ENi:1_{i}"], [f"EN:1_{i}"]))
        for j in range(1, self.x):
            rcts.add(
                SingleReaction([f"EN:{j}_{i}"], [f"ENi:{j+1}_{i}"], [f"EN:{j+1}_{i}"])
            )

        indices = list(range(1, self.y + 1))
        for comb in itertools.combinations(indices, self.z):
            reactants = []
            for i in comb:
                reactants.append(f"EN:{self.x}_{i}")
            rcts.add(SingleReaction(reactants, ["h"], ["TF"]))

    def generate(self):

        print(f"# Generated for: x = {self.x}, y = {self.y}, z = {self.z}")

        print("options { use-context-automaton; make-progressive; };")
        print("reactions {")

        for i in range(1, self.y + 1):
            self.generate_reactions_for_component(i)

        rcts_0 = self.generate_agent_zero()

        print("proc0 {")
        print(rcts_0)
        print("};")

        for proc, reactions in self.reactions.items():
            print(f"proc{proc} {{")
            print(reactions)
            print("};")

        print("};")

        self.generate_automaton(self.n)

    def generate_automaton(self, n):

        aut = self.automaton

        for i in range(0, (4 * n + 1)):
            aut.add_state(f"q{i}")

        aut.set_init_state("q0")

        aut.add_transition(
            Transition("q0", "q1", "", [(f"proc{i}", ["GF"]) for i in range(0, n + 1)])
        )

        for i in range(0, n):  # 0, ..., n-1
            aut.add_transition(
                Transition(f"q{4*i+1}", f"q{4*i+2}", "", [(f"proc{i+1}", [])])
            )
            aut.add_transition(
                Transition(
                    f"q{4*i+2}",
                    f"q{4*i+3}",
                    "",
                    [(f"proc{i}", []) for i in range(0, n + 1)],
                )
            )
            aut.add_transition(
                Transition(f"q{4*i+3}", f"q{4*i+4}", "", [(f"proc{i+1}", [])])
            )

        for i in range(0, n - 1):  # 0, ..., n-2
            aut.add_transition(
                Transition(
                    f"q{4*i+4}",
                    f"q{4*i+5}",
                    "",
                    [(f"proc{i}", []) for i in range(0, n + 1)],
                )
            )

        aut.add_transition(
            Transition(f"q{4*n}", "q1", "", [(f"proc{i}", []) for i in range(0, n + 1)])
        )

        print(aut)


def main():
    if len(sys.argv) < 1 + 4:
        print(f"Usage: {sys.argv[0]} <x> <y> <z> <n>")
        print("\twhere x,y,z >= 2 and y >= z")
        sys.exit(1)

    g = DRSGenerator(x=int(sys.argv[1]), y=int(sys.argv[2]), z=int(sys.argv[3]), n=int(sys.argv[4]))


if __name__ == "__main__":
    main()
