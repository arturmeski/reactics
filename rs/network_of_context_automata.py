from sys import exit

class NetworkOfContextAutomata(object):
    
    def __init__(self, context_automata):
        self.automata = list(context_automata)

    @property
    def number_of_automata(self):
        return len(self.automata)

    def show(self):
        for ca in self.automata:
            print()
            ca.show()

    def add(self, aut):
        self.automata.append(aut)
