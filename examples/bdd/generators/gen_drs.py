#!/usr/bin/env python

import sys


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
        return "{" + f"{self.get_reactants()}, {self.get_inhibitors()} -> {self.get_products()}" + "};"


class Reactions:
    def __init__(self):
        self.reactions = set()

    def add(self, reaction):
        self.reactions.add(reaction)

    def __str__(self):
        ret = ""
        for r in self.reactions:
            ret += f"{r}\n"
        return ret


class DRSGenerator:
    def __init__(self, x, y, z):
        assert y >= z
        assert x >= 2 and y >= 2 and z >= 2
        self.x = x
        self.y = y
        self.z = z
        self.reactions = {}

        self.generate()

    def generate_reactions_for_component(self, i):
        self.reactions.setdefault(i, Reactions())
        rcts = self.reactions[i]
        rcts.add(SingleReaction(["GF"], ["h"], ["GF"]))
        rcts.add(SingleReaction(["GF"], ["h", f"RTK{i}"], ["RTK"]))
        rcts.add(SingleReaction(["RTK"], [f"ENi:1_{i}"], [f"EN:1_{i}"]))
        for j in range(1, self.x):
            rcts.add(SingleReaction([f"EN:{j}_{i}"], [f"ENi:{j+1}_{i}"], [f"EN:{j+1}_{i}"]))

    def generate(self):
        for i in range(1, self.y):
            self.generate_reactions_for_component(i)

        for proc, reactions in self.reactions.items():
            print(f"proc={proc}")
            print(reactions)


def main():
    if len(sys.argv) < 1 + 2:
        print(f"Usage: {sys.argv[0]} <x> <y> <z>")
        print("\twhere x,y,z >= 2 and y >= z")
        sys.exit(1)

    g = DRSGenerator(x=int(sys.argv[1]), y=int(sys.argv[2]), z=int(sys.argv[3]))


if __name__ == "__main__":
    main()
