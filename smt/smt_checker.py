"""
SMT-based Model Checking Module for RS
"""

from z3 import *
from time import time
from sys import stdout

class SmtChecker(object):

    def __init__(self, rs):

        ##############################################################
        # Encoded RS
        ##############################################################
        rs.sanity_check()
        self.reaction_system = rs

        ##############################################################
        # SMT variables
        ##############################################################
        self.v = []
        self.v_init = []

        #self.vSucc = []
        #self.vSuccInit = []

        self.v_ctx = []

        self.next_level_to_encode = 0

        ##############################################################
        # SMT solver instance
        ##############################################################
        self.solver = Solver()

    #def smtVar(self, level, entityID, primed=False):
    #    return "?"

    def prepare_context_variables(self):
        """Encodes all the context variables"""

        level = self.next_level_to_encode

        variables = []
        for entity in self.reaction_system.background_set:
            variables.append(Bool("C"+str(level)+"_"+entity))

        self.v_ctx.append(variables)

    def prepare_state_variables(self):
        """Encodes all the state variables (including successors)"""

        level = self.next_level_to_encode

        variables = []
        #variablesSucc = []
        for entity in self.reaction_system.background_set:
            variables.append(Bool("L"+str(level)+"_"+entity))
            #variablesSucc.append(Bool("R"+str(level)+"_"+entity))

        self.v.append(variables)
        #self.vSucc.append(variablesSucc)

        self.v_init.append(Bool("L"+str(level)+"_Init"))
        #self.vSuccInit.append(Bool("R"+str(level)+"_Init"))

    def prepare_all_variables(self):
        """Encodes all the variables"""

        self.prepare_state_variables()
        self.prepare_context_variables()
        self.next_level_to_encode += 1

    def enc_init_state(self, level):
        """Encodes the initial state at the given level"""

        init_state_enc = self.v_init[level] 

        for v in self.v[level]:
            init_state_enc = simplify(And(init_state_enc, Not(v)))

        return init_state_enc

    def enc_init_contexts(self, level):
        """Encodes the initial contexts set at the given level"""

        init_contexts_set_enc = False # Or

        for ctx in self.reaction_system.init_contexts:
            single_ctx_enc = True # And
            
            not_ctx_entities = list(range(0, len(self.reaction_system.background_set)))
            for entity in ctx:
                single_ctx_enc = simplify(And(single_ctx_enc, self.v_ctx[level][entity]))
                not_ctx_entities.remove(entity)

            for entity in not_ctx_entities:
                single_ctx_enc = simplify(And(single_ctx_enc, Not(self.v_ctx[level][entity])))

            init_contexts_set_enc = simplify(Or(init_contexts_set_enc, single_ctx_enc))

        #print("initContextSetEnc: " + repr(initContextsSetEnc))
        return init_contexts_set_enc

    def enc_not_allowed_contexts(self, level):
        """Encodes all the context entities that are not allowed in the context sets"""

        bg_set = set(range(0,len(self.reaction_system.background_set)))
        ctx_ent_set = set(self.reaction_system.context_entities)

        not_ctx_ent_set = bg_set.difference(ctx_ent_set)

        enc = True
        for entity in not_ctx_ent_set:
            enc = simplify(And(enc, Not(self.v_ctx[level][entity])))

        return enc

    def enc_enabledness(self, level, prod_entity):
        """Encodes the enabledness condition for a given level and a given entity"""

        rcts_for_prod_entity = self.reaction_system.get_reactions_by_product()[prod_entity]

        if rcts_for_prod_entity == []:
            return False

        #encInitEnab = simplify(Or(And(self.vInit[level], self.encInitContexts(level)), 
        #        And(Not(self.vInit[level]), self.encNotAllowedContexts(level))))

        enc_rct_prod = False
        for ri_pair in rcts_for_prod_entity: # reactants-inhibitors pair
            enc_reactants = True
            enc_inhibitors = True
            for reactant in ri_pair[0]:
                enc_reactants = simplify(And(enc_reactants, 
                                            Or(self.v[level][reactant], self.v_ctx[level][reactant])))
            for inhibitor in ri_pair[1]:
                enc_inhibitors = simplify(And(enc_inhibitors, 
                                             Not(Or(self.v[level][inhibitor], self.v_ctx[level][inhibitor]))))

            enc_rct_prod = simplify(Or(enc_rct_prod, And(enc_reactants, enc_inhibitors)))

        #print("encEnabledness(" + repr(prodEntity) + "): " + repr(simplify(And(encInitEnab, encRctProd))))
        #return simplify(And(encInitEnab, encRctProd))
        return enc_rct_prod

    def enc_entity_production(self, level, prod_entity):
        """Encodes the production of a given entity from a given level at level+1"""

        enc_enab_cond = self.enc_enabledness(level, prod_entity)

        enc_ent_prod = Or(And(enc_enab_cond, self.v[level+1][prod_entity]),
                And(Not(enc_enab_cond), Not(self.v[level+1][prod_entity])))

        return enc_ent_prod

    def enc_transition_relation(self, level):
        """Encodes the transition relation"""

        unused_entities = list(range(0,len(self.reaction_system.background_set)))

        enc_trans = True

        for prod_entity in self.reaction_system.get_reactions_by_product():
            unused_entities.remove(prod_entity)
    
            enc_trans = simplify(And(enc_trans, self.enc_entity_production(level, prod_entity)))

        enc_trans = simplify(And(enc_trans, Not(self.v_init[level+1])))

        for prod_entity in unused_entities:
            enc_trans = simplify(And(enc_trans, Not(self.v[level+1][prod_entity])))

        if level == 0:
            enc_init_enab = self.enc_init_contexts(level)
        else: # level > 0:
            enc_init_enab = self.enc_not_allowed_contexts(level)

        #encInitEnab = simplify(Or(And(self.vInit[level], self.encInitContexts(level)), 
        #        And(Not(self.vInit[level]), self.encNotAllowedContexts(level))))

        enc_trans = simplify(And(enc_trans, enc_init_enab))

        return enc_trans

    def enc_state(self, level, state):
        """Encodes the state at the given level"""

        enc = Not(self.v_init[level])

        state_ids = self.reaction_system.get_state_ids(state)

        for entity in state_ids:
            enc = And(enc, self.v[level][entity])

        not_in_state = set(range(0, len(self.reaction_system.background_set)))
        not_in_state = not_in_state.difference(set(state_ids))

        for entity in not_in_state:
            enc = And(enc, Not(self.v[level][entity]))

        return enc

    def decode_witness(self, max_level):

        m = self.solver.model()

        for level in range(0,max_level+1):

            print("\n[Level=" + repr(level) + "]")

            if repr(m[self.v_init[level]]) == "True":
                print("** Initial state")

            print("State:\n{"),
            for var_id in range(0, len(self.v[level])):
                if repr(m[self.v[level][var_id]]) == "True":
                    print("\t" + self.reaction_system.get_entity_name(var_id)),
            print("}")

            if level != max_level:
                print("Context set:"),
                print("{"),
                for var_id in range(0, len(self.v[level])):
                    if repr(m[self.v_ctx[level][var_id]]) == "True":
                        print("\t" + self.reaction_system.get_entity_name(var_id)),
                print("}")


    def check_reachability(self, state, print_witness=True, print_time=False):
        """Main testing function"""

        if print_time:
            start = time()

        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        current_level = 0

        while True:
            #print("Level: " + str(current_level))
            print("\rLevel: " + str(current_level)),
            stdout.flush()

            self.prepare_all_variables()

            # reachability test:
            self.solver.push()
            self.solver.add(self.enc_state(current_level,state))

            result = self.solver.check()
            print(result)
            if result == sat:
                print("\nSAT")
                if print_witness:
                    self.decode_witness(current_level)
                break
            else:
                self.solver.pop()
           
            self.solver.add(self.enc_transition_relation(current_level))

            current_level += 1

        if print_time:
            stop = time()
            print("Time: " + repr(stop-start))

#
# class SmtCheckerPGRS(object):
#
#     def __init__(self, rs):
#
#         ##############################################################
#         # Encoded RS
#         ##############################################################
#         rs.sanity_check()
#         self.reaction_system = rs
#
#         ##############################################################
#         # SMT variables
#         ##############################################################
#         self.v = []
#         self.v_init = []
#
#         #self.vSucc = []
#         #self.vSuccInit = []
#
#         self.v_ctx = []
#
#         self.next_level_to_encode = 0
#
#         ##############################################################
#         # SMT solver instance
#         ##############################################################
#         self.solver = Solver()
#
#     #def smtVar(self, level, entityID, primed=False):
#     #    return "?"
#
#     def prepare_context_variables(self):
#         """Encodes all the context variables"""
#
#         level = self.next_level_to_encode
#
#         variables = []
#         for entity in self.reaction_system.background_set:
#             variables.append(Bool("C"+str(level)+"_"+entity))
#
#         self.v_ctx.append(variables)
#
#     def prepare_state_variables(self):
#         """Encodes all the state variables (including successors)"""
#
#         level = self.next_level_to_encode
#
#         variables = []
#         #variablesSucc = []
#         for entity in self.reaction_system.background_set:
#             variables.append(Bool("L"+str(level)+"_"+entity))
#             #variablesSucc.append(Bool("R"+str(level)+"_"+entity))
#
#         self.v.append(variables)
#         #self.vSucc.append(variablesSucc)
#
#         self.v_init.append(Bool("L"+str(level)+"_Init"))
#         #self.vSuccInit.append(Bool("R"+str(level)+"_Init"))
#
#     def prepare_all_variables(self):
#         """Encodes all the variables"""
#
#         self.prepare_state_variables()
#         self.prepare_context_variables()
#         self.next_level_to_encode += 1
#
#     def enc_init_state(self, level):
#         """Encodes the initial state at the given level"""
#
#         init_state_enc = self.v_init[level]
#
#         for v in self.v[level]:
#             init_state_enc = simplify(And(init_state_enc, Not(v)))
#
#         return init_state_enc
#
#     def enc_init_contexts(self, level):
#         """Encodes the initial contexts set at the given level"""
#
#         init_contexts_set_enc = False # Or
#
#         for ctx in self.reaction_system.init_contexts:
#             single_ctx_enc = True # And
#
#             not_ctx_entities = list(range(0, len(self.reaction_system.background_set)))
#             for entity in ctx:
#                 single_ctx_enc = simplify(And(single_ctx_enc, self.v_ctx[level][entity]))
#                 not_ctx_entities.remove(entity)
#
#             for entity in not_ctx_entities:
#                 single_ctx_enc = simplify(And(single_ctx_enc, Not(self.v_ctx[level][entity])))
#
#             init_contexts_set_enc = simplify(Or(init_contexts_set_enc, single_ctx_enc))
#
#         #print("initContextSetEnc: " + repr(initContextsSetEnc))
#         return init_contexts_set_enc
#
#     def enc_not_allowed_contexts(self, level):
#         """Encodes all the context entities that are not allowed in the context sets"""
#
#         bg_set = set(range(0,len(self.reaction_system.background_set)))
#         ctx_ent_set = set(self.reaction_system.context_entities)
#
#         not_ctx_ent_set = bg_set.difference(ctx_ent_set)
#
#         enc = True
#         for entity in not_ctx_ent_set:
#             enc = simplify(And(enc, Not(self.v_ctx[level][entity])))
#
#         return enc
#
#     def enc_enabledness(self, level, prod_entity):
#         """Encodes the enabledness condition for a given level and a given entity"""
#
#         rcts_for_prod_entity = self.reaction_system.get_reactions_by_product()[prod_entity]
#
#         if rcts_for_prod_entity == []:
#             return False
#
#         #encInitEnab = simplify(Or(And(self.vInit[level], self.encInitContexts(level)),
#         #        And(Not(self.vInit[level]), self.encNotAllowedContexts(level))))
#
#         enc_rct_prod = False
#         for ri_pair in rcts_for_prod_entity: # reactants-inhibitors pair
#             enc_reactants = True
#             enc_inhibitors = True
#             for reactant in ri_pair[0]:
#                 enc_reactants = simplify(And(enc_reactants,
#                                             Or(self.v[level][reactant], self.v_ctx[level][reactant])))
#             for inhibitor in ri_pair[1]:
#                 enc_inhibitors = simplify(And(enc_inhibitors,
#                                              Not(Or(self.v[level][inhibitor], self.v_ctx[level][inhibitor]))))
#
#             enc_rct_prod = simplify(Or(enc_rct_prod, And(enc_reactants, enc_inhibitors)))
#
#         #print("encEnabledness(" + repr(prodEntity) + "): " + repr(simplify(And(encInitEnab, encRctProd))))
#         #return simplify(And(encInitEnab, encRctProd))
#         return enc_rct_prod
#
#     def enc_entity_production(self, level, prod_entity):
#         """Encodes the production of a given entity from a given level at level+1"""
#
#         enc_enab_cond = self.enc_enabledness(level, prod_entity)
#
#         enc_ent_prod = Or(And(enc_enab_cond, self.v[level+1][prod_entity]),
#                 And(Not(enc_enab_cond), Not(self.v[level+1][prod_entity])))
#
#         return enc_ent_prod
#
#     def enc_transition_relation(self, level):
#         """Encodes the transition relation"""
#
#         unused_entities = list(range(0,len(self.reaction_system.background_set)))
#
#         enc_trans = True
#
#         for prod_entity in self.reaction_system.get_reactions_by_product():
#             unused_entities.remove(prod_entity)
#
#             enc_trans = simplify(And(enc_trans, self.enc_entity_production(level, prod_entity)))
#
#         enc_trans = simplify(And(enc_trans, Not(self.v_init[level+1])))
#
#         for prod_entity in unused_entities:
#             enc_trans = simplify(And(enc_trans, Not(self.v[level+1][prod_entity])))
#
#         if level == 0:
#             enc_init_enab = self.enc_init_contexts(level)
#         else: # level > 0:
#             enc_init_enab = self.enc_not_allowed_contexts(level)
#
#         #encInitEnab = simplify(Or(And(self.vInit[level], self.encInitContexts(level)),
#         #        And(Not(self.vInit[level]), self.encNotAllowedContexts(level))))
#
#         enc_trans = simplify(And(enc_trans, enc_init_enab))
#
#         return enc_trans
#
#     def enc_state(self, level, state):
#         """Encodes the state at the given level"""
#
#         enc = Not(self.v_init[level])
#
#         state_ids = self.reaction_system.get_state_ids(state)
#
#         for entity in state_ids:
#             enc = And(enc, self.v[level][entity])
#
#         not_in_state = set(range(0, len(self.reaction_system.background_set)))
#         not_in_state = not_in_state.difference(set(state_ids))
#
#         for entity in not_in_state:
#             enc = And(enc, Not(self.v[level][entity]))
#
#         return enc
#
#     def decode_witness(self, max_level):
#
#         m = self.solver.model()
#
#         for level in range(0,max_level+1):
#
#             print("\n[Level=" + repr(level) + "]")
#
#             if repr(m[self.v_init[level]]) == "True":
#                 print("** Initial state")
#
#             print("State:\n{"),
#             for var_id in range(0, len(self.v[level])):
#                 if repr(m[self.v[level][var_id]]) == "True":
#                     print("\t" + self.reaction_system.get_entity_name(var_id)),
#             print("}")
#
#             if level != max_level:
#                 print("Context set:"),
#                 print("{"),
#                 for var_id in range(0, len(self.v[level])):
#                     if repr(m[self.v_ctx[level][var_id]]) == "True":
#                         print("\t" + self.reaction_system.get_entity_name(var_id)),
#                 print("}")
#
#
#     def check_reachability(self, state, print_witness=True, print_time=False):
#         """Main testing function"""
#
#         if print_time:
#             start = time()
#
#         self.prepare_all_variables()
#         self.solver.add(self.enc_init_state(0))
#         current_level = 0
#
#         while True:
#             #print("Level: " + str(current_level))
#             print("\rLevel: " + str(current_level)),
#             stdout.flush()
#
#             self.prepare_all_variables()
#
#             # reachability test:
#             self.solver.push()
#             self.solver.add(self.enc_state(current_level,state))
#
#             result = self.solver.check()
#             print(result)
#             if result == sat:
#                 print("\nSAT")
#                 if print_witness:
#                     self.decode_witness(current_level)
#                 break
#             else:
#                 self.solver.pop()
#
#             self.solver.add(self.enc_transition_relation(current_level))
#
#             current_level += 1
#
#         if print_time:
#             stop = time()
#             print("Time: " + repr(stop-start))