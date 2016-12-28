from sys import exit

class NetworkOfContextAutomata(object):
    
    def __init__(self, context_automata):
        self.cas = list(context_automata)

    def show(self):
        for ca in self.cas:
            print()
            ca.show()

    def add(self, aut):
        self.cas.append(aut)
