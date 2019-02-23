
class ReactionSystemWithNetworkOfAutomata(object):
    
    def __init__(self, reaction_system, context_automata):
        self.rs = reaction_system
        self.cas = context_automata

    def show(self, soft=False):
        self.rs.show(soft)
        self.cas.show()

# EOF