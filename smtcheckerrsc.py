"""
SMT-based Model Checking Module for RS with Concentrations and Context Automaton
"""

from z3 import *
from time import time
from sys import stdout

class SmtCheckerRSC(object):

    def __init__(self, rsca):

        rsca.sanity_check()
        
        self.rs = rsca.rs
        self.ca = rsca.ca        

        self.v = []
        self.v_ctx = []
        self.ca_state = []
        self.next_level_to_encode = 0

        self.solver = Solver()

    def prepare_all_variables(self):
        """Encodes all the variables"""

        self.prepare_state_variables()
        self.prepare_context_variables()
        self.next_level_to_encode += 1
        
    def prepare_context_variables(self):
        """Encodes all the context variables"""

        level = self.next_level_to_encode

        variables = []
        for entity in self.rs.background_set:
            variables.append(Bool("C"+str(level)+"_"+entity))

        self.v_ctx.append(variables)

    def prepare_state_variables(self):
        """Encodes all the state variables"""

        level = self.next_level_to_encode

        variables = []
        for entity in self.rs.background_set:
            variables.append(Bool("L"+str(level)+"_"+entity))
        self.v.append(variables)
        
        self.ca_state.append(Int("CA"+str(level)+"_state"))

    def enc_init_state(self, level):
        """Encodes the initial state at the given level"""

        rs_init_state_enc = True

        for v in self.v[level]:
            rs_init_state_enc = simplify(And(rs_init_state_enc, Not(v))) # the initial state is empty

        ca_init_state_enc = self.ca_state[level] == self.ca.get_init_state_id()
        
        init_state_enc = simplify(And(rs_init_state_enc, ca_init_state_enc))

        return init_state_enc

    def enc_enabledness(self, level, prod_entity):
        """Encodes the enabledness condition for a given level and a given entity"""

        rcts_for_prod_entity = self.rs.get_reactions_by_product()[prod_entity]

        if rcts_for_prod_entity == []:
            return False

        enc_rct_prod = False
        for reactants,inhibitors in rcts_for_prod_entity:
            enc_reactants = True
            enc_inhibitors = True
            for reactant in reactants:
                enc_reactants = simplify(And(enc_reactants, 
                                            Or(self.v[level][reactant], self.v_ctx[level][reactant])))
            for inhibitor in inhibitors:
                enc_inhibitors = simplify(And(enc_inhibitors, 
                                             Not(Or(self.v[level][inhibitor], self.v_ctx[level][inhibitor]))))

            enc_rct_prod = simplify(Or(enc_rct_prod, And(enc_reactants, enc_inhibitors)))

        return enc_rct_prod

    def enc_entity_production(self, level, prod_entity):
        """Encodes the production of a given entity from a given level at level+1"""

        enc_enab_cond = self.enc_enabledness(level, prod_entity)

        enc_ent_prod = Or(And(enc_enab_cond, self.v[level+1][prod_entity]),
                And(Not(enc_enab_cond), Not(self.v[level+1][prod_entity])))

        return simplify(enc_ent_prod)
        
    def enc_transition_relation(self, level):
        return simplify(And(self.enc_rs_trans(level), self.enc_automaton_trans(level)))

    def enc_rs_trans(self, level):
        """Encodes the transition relation"""

        unused_entities = list(range(len(self.rs.background_set)))

        enc_trans = True

        for prod_entity in self.rs.get_reactions_by_product():
            unused_entities.remove(prod_entity)
    
            enc_trans = simplify(And(enc_trans, self.enc_entity_production(level, prod_entity)))

        for prod_entity in unused_entities:
            enc_trans = simplify(And(enc_trans, Not(self.v[level+1][prod_entity])))

        return enc_trans
    
    def enc_automaton_trans(self, level):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = False
    
        for src,ctx,dst in self.ca.transitions:
                src_enc = self.ca_state[level] == src
                dst_enc = self.ca_state[level+1] == dst
                
                all_ent = set(range(len(self.rs.background_set)))
                incl_ctx = ctx
                excl_ctx = all_ent - incl_ctx
                
                ctx_enc = True
                
                for c in incl_ctx:
                    ctx_enc = simplify(And(ctx_enc, self.v_ctx[level][c]))
                for c in excl_ctx:
                    ctx_enc = simplify(And(ctx_enc, Not(self.v_ctx[level][c])))
                
                cur_trans = simplify(And(src_enc, ctx_enc, dst_enc))
                
                enc_trans = simplify(Or(enc_trans, cur_trans))
        
        return enc_trans

    def enc_state(self, level, state):
        """Encodes the state at the given level"""

        enc = True

        state_ids = self.rs.get_state_ids(state)

        for entity in state_ids:
            enc = And(enc, self.v[level][entity])

        not_in_state = set(range(len(self.rs.background_set)))
        not_in_state = not_in_state.difference(set(state_ids))

        for entity in not_in_state:
            enc = And(enc, Not(self.v[level][entity]))

        return enc

    def enc_non_exclusive_state(self, level, state):
        """Encodes the state at the given level"""

        enc = True

        state_ids = self.rs.get_state_ids(state)

        for entity in state_ids:
            enc = And(enc, self.v[level][entity])

        return enc

    def decode_witness(self, max_level, print_model=False):

        m = self.solver.model()

        if print_model:
            print(m)

        for level in range(max_level+1):

            print("\n[Level=" + repr(level) + "]")

            print("  State: {", end=""),
            for var_id in range(len(self.v[level])):
                if repr(m[self.v[level][var_id]]) == "True":
                    print(" " + self.rs.get_entity_name(var_id), end="")
            print(" }")

            if level != max_level:
                print("  Context set: ", end="")
                print("{", end="")
                for var_id in range(len(self.v[level])):
                    if repr(m[self.v_ctx[level][var_id]]) == "True":
                        print(" " + self.rs.get_entity_name(var_id), end="")
                print(" }")

    def check_reachability(self, state, print_witness=True, print_time=False):
        """Main testing function"""

        if print_time:
            start = time()

        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        current_level = 0

        while True:
            print("\r[i] Level: " + str(current_level), end="")
            stdout.flush()

            self.prepare_all_variables()

            # reachability test:
            self.solver.push()
            self.solver.add(self.enc_state(current_level,state))

            result = self.solver.check()
            if result == sat:
                print("\n[+] SAT at level=" + str(current_level))
                if print_witness:
                    self.decode_witness(current_level)
                break
            else:
                self.solver.pop()
           
            self.solver.add(self.enc_transition_relation(current_level))

            current_level += 1

        if print_time:
            stop = time()
            print()
            print("[i] Time: " + repr(stop-start))
            
