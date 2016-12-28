"""
SMT-based Model Checking Module for RS with Context Automaton
"""

from z3 import *
from time import time,sleep
from sys import stdout
import resource

# def simplify(x):
#     return x

class SmtCheckerDistribRS(object):

    def __init__(self, drs, debug_level=1):

        print("[i] Initialising the SMT module")

        drs.sanity_check()
        
        self.solver = Solver()
        
        self.debug_level = debug_level
        self.drs = drs
        self.n_components = self.drs.components_count

        # encoding variables
        self.v = [] # level -> component -> variables
        self.v_ctx = []
        self.v_act = [] # indicators of which component is active
        self.ca_state = []

        self.level_to_encode = 0
        
    def prepare_all_variables(self):
        """Encodes the required variables"""

        self.prepare_state_variables()
        self.prepare_context_variables()
        self.prepare_activity_variables()
        
        self.level_to_encode += 1 # prepare for the next invocation
        
    def prepare_context_variables(self):
        """Encodes the context variables"""

        level = self.level_to_encode

        if self.debug_level > 1:
            print("[ii] Preparing context variables for level=" + str(level))
            
        level_variables = []
        
        for i in range(self.n_components):

            comp_variables = []
            
            for entity in self.drs.background_set:
                comp_variables.append(Bool("Ctx"+str(level)+"V"+str(i)+"_"+entity))
            
            level_variables.append(comp_variables)

        self.v_ctx.append(level_variables)
        
    def prepare_activity_variables(self):
        """Encodes the activity variables"""

        level = self.level_to_encode
        
        if self.debug_level > 1:
            print("[ii] Preparing activity variables for level=" + str(level))

        level_variables = []
        
        for i in range(self.n_components):
            # L - level, A - activity indicator
            level_variables.append(Bool("L"+str(level)+"A"+str(i)))
            
        self.v_act.append(level_variables)

    def prepare_state_variables(self):
        """Encodes all the state variables"""

        level = self.level_to_encode

        if self.debug_level > 1:
            print("[ii] Preparing state variables for level=" + str(level))

        level_variables = [] # level vars
        
        for i in range(self.n_components):

            comp_variables = []
            
            for entity in self.drs.background_set:
                # L - level, V - component
                comp_variables.append(Bool("L"+str(level)+"V"+str(i)+"_"+entity)) 
            
            level_variables.append(comp_variables)

        self.v.append(level_variables)

        # single state variable for CA
        self.ca_state.append(Int("CA"+str(level)+"_state"))

    def enc_init_state(self, level):
        """Encodes the initial state at the given level"""

        if self.debug_level > 1:
            print("[ii] Encoding the initial state for level=" + str(level))

        rs_init_state_enc = True

        for i in range(self.n_components):
            for v in self.v[level][i]:
                rs_init_state_enc = simplify(And(rs_init_state_enc, Not(v))) # the initial state is empty

        ca_init_state_enc = self.ca_state[level] == self.drs.get_init_state_id()
        init_state_enc = simplify(And(rs_init_state_enc, ca_init_state_enc))

        # print ("init_state_enc:\n", init_state_enc)

        return init_state_enc

    def enc_enabledness(self, level, prod_entity, component_id):
        """Encodes the enabledness condition for a given level and a given entity"""

        rcts_for_prod_entity = self.drs.get_reactions_by_product(component_id)[prod_entity]

        if rcts_for_prod_entity == []:
            return False

        enc_rct_prod = False
        for reactants,inhibitors in rcts_for_prod_entity:

    
            enc_reactants = True
            for reactant in reactants:
                
                enc_active_reactants = False
                for i in range(self.n_components):
                    enc_active_reactants = simplify(Or(enc_active_reactants, 
                            And(  Or(self.v[level][i][reactant], self.v_ctx[level][i][reactant]),  self.v_act[level][i]  )))
                
                enc_reactants = And(enc_reactants, enc_active_reactants)
            
    
            enc_inhibitors = True
            for inhibitor in inhibitors:
            
                enc_active_inhibitors = True
                for i in range(self.n_components):
                    enc_active_inhibitors = simplify(And(enc_active_inhibitors, 
                            And(
                                Or( And(Not(self.v[level][i][inhibitor]), Not(self.v_ctx[level][i][inhibitor])), Not(self.v_act[level][i]) )
                            )))

                enc_inhibitors = simplify(And(enc_inhibitors, enc_active_inhibitors))

            # print("--> enc_inhibitors\n", enc_inhibitors)
            enc_rct_prod = Or(enc_rct_prod, And(enc_reactants, enc_inhibitors))

        # print("enc_rct_prod:\n", enc_rct_prod)

        enc_rct_prod = simplify(enc_rct_prod)

        return enc_rct_prod

    def enc_entity_production(self, level, prod_entity, component_id):
        """Encodes the production of a given entity at level+1 from a given level"""

        enc_enab_cond = self.enc_enabledness(level, prod_entity, component_id)

        enc_base_ent_prod = simplify(Or(And(enc_enab_cond, self.v[level+1][component_id][prod_entity]),
                And(Not(enc_enab_cond), Not(self.v[level+1][component_id][prod_entity]))))

        enc_active_ent_prod = simplify(And(self.v_act[level][component_id], enc_base_ent_prod))
        enc_inactive_ent_prod = simplify(And(
                Not(self.v_act[level][component_id]), 
                self.v[level][component_id][prod_entity] == self.v[level+1][component_id][prod_entity]))
        
        enc_ent_prod = Or(enc_active_ent_prod, enc_inactive_ent_prod)

        # print("enc_ent_prod:\n", enc_ent_prod)

        return simplify(enc_ent_prod)
        
    def enc_rs_trans(self, level):
        """Encodes the transition relation"""

        enc_trans = True

        for component_id in range(self.n_components):

            print("\rEncoding for reactions: %d/%d" % (component_id,self.n_components-1), flush=True, end="")
                
            unused_entities = list(range(len(self.drs.background_set)))

            for prod_entity in self.drs.get_reactions_by_product(component_id):
                unused_entities.remove(prod_entity)
    
                enc_trans = simplify(And(enc_trans, self.enc_entity_production(level, prod_entity, component_id)))

            for prod_entity in unused_entities:
                enc_trans = simplify(And(enc_trans, Not(self.v[level+1][component_id][prod_entity])))

        print()
        # print("enc_rs_trans:\n", enc_trans)
        
        enc_trans = simplify(enc_trans)
        
        return enc_trans
    
    def enc_automaton_trans(self, level):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = False
    
        i = 0
        for src,(components,ctx_set),dst in self.drs.transitions:
                src_enc = self.ca_state[level] == src
                dst_enc = self.ca_state[level+1] == dst
                
                print("\rEncoding for context automaton: %d/%d" % (i,len(self.drs.transitions)-1), flush=True, end="")
                
                i = i + 1
                
                # contexts {
                ctx_set_enc = True
                for comp_id in range(self.n_components):

                    all_ent = set(range(len(self.drs.background_set)))
                    incl_ctx = ctx_set[comp_id]
                    excl_ctx = all_ent - incl_ctx
                
                    ctx_enc = True
                
                    for c in incl_ctx:
                        ctx_enc = And(ctx_enc, self.v_ctx[level][comp_id][c])
                    for c in excl_ctx:
                        ctx_enc = And(ctx_enc, Not(self.v_ctx[level][comp_id][c]))
                        
                    ctx_set_enc = And(ctx_set_enc, ctx_enc)
                # } contexts
                
                # active components {
                all_active = set(range(self.n_components))
                incl_comp = components
                excl_comp = all_active - incl_comp
                       
                active_components_enc = True
                for comp_id in incl_comp:
                    active_components_enc = And(active_components_enc, self.v_act[level][comp_id])
                for comp_id in excl_comp:
                    active_components_enc = And(active_components_enc, Not(self.v_act[level][comp_id]))
                # } active components
                
                cur_trans = And(src_enc, ctx_set_enc, active_components_enc, dst_enc)
                
                enc_trans = Or(enc_trans, cur_trans)
        
        print()
        
        enc_trans = simplify(enc_trans)
        
        # print("enc_automaton_trans:\n", enc_trans)
        return enc_trans

    def enc_transition_relation(self, level):
        
        rs_enc = self.enc_rs_trans(level)
        aut_enc = self.enc_automaton_trans(level)
        
        print("Conjunction...", flush=True, end="")
        
        c = simplify(And(rs_enc, aut_enc))
        
        print("done.")
        
        return c
        
    def enc_state(self, level, global_state):
        """Encodes the state at the given level"""

        if len(global_state) != self.n_components:
            print("EEE: Wrong size of the global state! " + "(is " + str(len(global_state)) + ", should be " + str(self.n_components) + ")")
            exit(1)

        enc = True

        if self.debug_level > 2:
            print("[iii] Encoding exclusive/exact global state " + str(global_state) + " for level=" + str(level))

        for i in range(self.n_components):
            local_state = global_state[i]
            
            local_state_ids = self.drs.get_state_ids(local_state)

            for entity in local_state_ids:
                enc = And(enc, self.v[level][i][entity])

            not_in_state = self.drs.set_of_background_ids - set(local_state_ids)

            for e_id in not_in_state:
                enc = simplify(And(enc, Not(self.v[level][i][e_id])))
        
        simplify(enc)
        # print("state:\n", enc)
        return enc

    def enc_inclusive_state(self, level, global_state):
        """Encodes the state at the given level"""

        if len(global_state) != self.n_components:
            print("EEE: Wrong size of the global state! " + "(is " + str(len(global_state)) + ", should be " + str(self.n_components) + ")")
            exit(1)

        enc = True

        if self.debug_level > 2:
            print("[iii] Encoding inclusive/general global state " + str(global_state) + " for level=" + str(level))

        for i in range(self.n_components):
            local_state = global_state[i]
            
            local_state_ids = self.drs.get_state_ids(local_state)

            for entity in local_state_ids:
                enc = And(enc, self.v[level][i][entity])
        
        simplify(enc)
        return enc

    def decode_witness(self, max_level, print_model=False):

        m = self.solver.model()

        print("\nWitness:")

        if print_model:
            print(m)

        for level in range(max_level+1):

            print("\n[Level=" + repr(level) + "]")

            #print(m)
            #print(self.v[level][0][2])
            #print(m[self.v[level][0][2]])

            print("  State: {", end=""),
            for c in range(self.n_components):
                print(" <", end="")
                for var_id in range(len(self.v[level][c])):
                    if repr(m[self.v[level][c][var_id]]) == "True":
                        print(" " + self.drs.get_entity_name(var_id), end="")
                print(" >", end="")
            print(" }")

            if level != max_level:
                print("  Context set: ", end="")
                print("{", end="")
                for c in range(self.n_components):
                    print(" <", end="")
                    for var_id in range(len(self.v[level][c])):
                        if repr(m[self.v_ctx[level][c][var_id]]) == "True":
                            print(" " + self.drs.get_entity_name(var_id), end="")
                    print(" >", end="")
                print(" }")
            
                print("  Active components:", end="")
                for c in range(self.n_components):
                    if repr(m[self.v_act[level][c]]) == "True":
                        print(" " + str(c), end="")
                print()
            


    def check_reachability(self, state, exclusive_state=False, print_witness=True, print_time=False, print_mem=False, max_level=100):
        """Reachability checking"""

        print("[i] Checking reachability...")

        if print_time:
            start = time()

        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        current_level = 0

        while True:

            self.prepare_all_variables()
                   
            print("-----[ Working at level=" + str(current_level) + " ]-----")
            stdout.flush()
       
             # reachability test:
            self.solver.push()
            print("[i] Adding the reachability test...")
            if exclusive_state == False:
                self.solver.add(self.enc_inclusive_state(current_level,state))
            else:
                self.solver.add(self.enc_state(current_level,state))
        
            result = self.solver.check()
            if result == sat:
                print("\n[+] SAT at level=" + str(current_level))
                if print_witness:
                    self.decode_witness(current_level)
                break
            else:
                self.solver.pop()
            
            print("[i] Unrolling the transition relation")
            self.solver.add(self.enc_transition_relation(current_level))

            print("-----[ level=" + str(current_level) + " done ]")
            current_level += 1
            
            if current_level > max_level:
                print("Stopping at level=" + str(max_level))
                break

        if print_time:
            stop = time()
            print()
            print("==== Time: " + repr(stop-start))

        if print_mem:
            usage=resource.getrusage(resource.RUSAGE_SELF)
            print("MEM: usertime=%s systime=%s mem=%sMB" % (usage[0],usage[1], (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2)))
