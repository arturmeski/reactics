"""
SMT-based Model Checking Module for RS with Concentrations and Context Automaton
"""

from z3 import *
from time import time
from sys import stdout
from itertools import chain
import resource
from colour import *

from logics import rsLTL_Encoder

# def simplify(x):
#     return x

def MAX(a, b):
    return If(a > b, a, b)

class SmtCheckerRSCParam(object):

    def __init__(self, rsca):
    
        rsca.sanity_check()

        if not rsca.is_concentr_and_param_compatible():
            raise RuntimeError("RS and CA with concentrations (and parameters) expected")
        
        self.rs = rsca.rs
        self.ca = rsca.ca

        self.initialise()
    
    
    def initialise(self):
        """Initialises all the variables used by the checker"""
        
        self.v = []
        self.v_ctx = []
        self.ca_state = []
        
        # intermediate products:
        self.v_improd = []

        self.v_improd_for_entities = []

        self.next_level_to_encode = 0

        self.producible_entities = self.rs.get_producible_entities()
        
        self.loop_position = Int("loop_position")
        
        self.solver = Solver() #For("QF_FD")
        
        self.verification_time = None        


    def reset(self):
        """Reinitialises the state of the checker"""
        
        self.initialise()
        
        
    def prepare_all_variables(self):
        """Prepares all the variables"""

        self.prepare_state_variables()
        self.prepare_context_variables()
        self.prepare_intermediate_product_variables()
        self.next_level_to_encode += 1
        
        
    def prepare_context_variables(self):
        """Prepares all the context variables"""

        level = self.next_level_to_encode

        variables = []
        for entity in self.rs.background_set:
            variables.append(Int("C"+str(level)+"_"+entity))

        self.v_ctx.append(variables)


    def prepare_state_variables(self):
        """Prepares all the state variables"""

        level = self.next_level_to_encode

        variables = []
        for entity in self.rs.background_set:
            variables.append(Int("L"+str(level)+"_"+entity))
        self.v.append(variables)
        
        self.ca_state.append(Int("CA"+str(level)+"_state"))


    def prepare_intermediate_product_variables(self):
        """
        Prepares the intermediate product variables
        carrying the individual concentration levels produced
        the reactions.

        These variables are used later on to encode the final
        concentration levels for all the entities
        """

        level = self.next_level_to_encode

        if level < 1:
            #
            # If we are at level==0, we add a dummy "level"
            # to match the indices of of the successors
            # which are always at level+1.
            #
            self.v_improd.append(None)
            self.v_improd_for_entities.append(None)
        else:

            reactions_dict = dict()
            number_of_reactions = len(self.rs.reactions)

            all_entities_dict = dict()

            for reaction in self.rs.reactions:
                *_, products = reaction

                reaction_id = self.rs.reactions.index(reaction)

                entities_dict = dict()
                for entity, conc in products:
                    varname = Int("IP" + str(level) + "_R" +
                                  str(reaction_id) + "_e" + str(entity))
                    entities_dict[entity] = varname

                    all_entities_dict.setdefault(entity, [])
                    all_entities_dict[entity].append(varname)

                reactions_dict[reaction_id] = entities_dict
            
            self.v_improd.append(reactions_dict)
            self.v_improd_for_entities.append(all_entities_dict)

            print(self.v_improd)

            print(self.v_improd_for_entities)
        
    def enc_concentration_levels_assertion(self, level):
        """
        Encodes assertions that (some) variables need to be >0
        
        We do not need to actually control all the variables,
        only those that can possibly go below 0.
        """
        
        enc_nz = True
        
        for e_i in range(len(self.rs.background_set)):
            v = self.v[level][e_i]
            v_ctx = self.v_ctx[level][e_i]
            e_max = self.rs.get_max_concentration_level(e_i)
            enc_nz = simplify(And(enc_nz, v >= 0, v_ctx >= 0, v <= e_max, v_ctx <= e_max))
        
        return enc_nz
        

    def enc_init_state(self, level):
        """Encodes the initial state at the given level"""

        rs_init_state_enc = True

        for v in self.v[level]:
            rs_init_state_enc = simplify(And(rs_init_state_enc, v == 0)) # the initial concentration levels are zeroed

        ca_init_state_enc = self.ca_state[level] == self.ca.get_init_state_id()
        
        init_state_enc = simplify(And(rs_init_state_enc, ca_init_state_enc))

        return init_state_enc
        
                
    def enc_transition_relation(self, level):
        return simplify(And(self.enc_rs_trans(level), self.enc_automaton_trans(level)))            


    def enc_rs_trans(self, level):
        """Encodes the transition relation"""

        #
        # IMPORTANT NOTE
        #
        # We need to make sure we do something about the UNUSED ENTITIES
        # that is, those that are never produced.
        # 
        # They should have concentration levels set to 0.
        #

        enc_trans = True

        for reaction in self.rs.reactions:
            
            reactants, inhibitors, products = reaction
            reaction_id = self.rs.reactions.index(reaction)
                        
            enc_reactants = True
            for entity, conc in reactants:
                enc_reactants = And(enc_reactants, 
                    Or(self.v[level][entity] >= conc, self.v_ctx[level][entity] >= conc))
            
            enc_inhibitors = True
            for entity, conc in inhibitors:
                enc_inhibitors = And(enc_inhibitors,
                    And(self.v[level][entity] < conc, self.v_ctx[level][entity] < conc))
                    
            enc_products = True
            #
            #
            #
            for entity, conc in products:
                enc_products = And(enc_products,
                    self.v_improd[level+1][reaction_id][entity] == conc)
            
            #
            # (R and I) iff P
            #
            enc_reaction = simplify(And(enc_reactants, enc_inhibitors) == enc_products)
            
            enc_trans = simplify(And(enc_trans, enc_reaction))
            
        print(enc_trans)

        #
        # TODO:
        #
        # Max of all the produced concentrations for each entity/product...
        
        enc_max_prod = True

        current_v_improd_for_entities = self.v_improd_for_entities[level+1]
        for entity, per_reaction_vars in current_v_improd_for_entities.items():

                # enc_max_single_ent = True

                #sorted_vars_by_conc = sorted(per_reaction_vars, key=lambda conc_var: conc_var[0])
                #list_of_vars = [v for c,v in sorted_vars_by_conc]

                print(per_reaction_vars, "--->", self.enc_max(per_reaction_vars))

        return enc_trans
    
    
    def enc_max(self, elements):

        if len(elements) == 1:
            return MAX(0, elements[0])

        elif len(elements) > 1:

            enc = 0
            for i in range(len(elements) - 1):
                enc = MAX(enc, MAX(elements[i], elements[i + 1]))

            return enc

        else:
            return None
            
    
    def enc_automaton_trans(self, level):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = False
    
        for src,ctx,dst in self.ca.transitions:
                src_enc = self.ca_state[level] == src
                dst_enc = self.ca_state[level+1] == dst
                
                all_ent = set(range(len(self.rs.background_set)))
                
                incl_ctx = set([e for e,c in ctx])
                excl_ctx = all_ent - incl_ctx
                
                ctx_enc = True
                
                for e,c in ctx:
                    ctx_enc = simplify(And(ctx_enc, self.v_ctx[level][e] == c))
                
                for e in excl_ctx:
                    ctx_enc = simplify(And(ctx_enc, self.v_ctx[level][e] == 0))
                
                cur_trans = simplify(And(src_enc, ctx_enc, dst_enc))
                enc_trans = simplify(Or(enc_trans, cur_trans))
        
        return enc_trans


    def enc_exact_state(self, level, state):
        """Encodes the state at the given level with the exact concentration values"""

        raise RuntimeError("Should not be used with RSC")

        # enc = True
        # used_entities_ids = self.rs.get_state_ids(state)
        #
        # for ent,conc in state:
        #     e_id = self.rs.get_entity_id(ent)
        #     enc = And(enc, self.v[level][e_id] == conc)
        #
        # not_in_state = set(range(len(self.rs.background_set)))
        # not_in_state = not_in_state.difference(set(used_entities_ids))
        #
        # for entity in not_in_state:
        #     enc = And(enc, self.v[level][entity] == 0)
        #
        # return simplify(enc)
        

    def enc_min_state(self, level, state):
        """Encodes the state at the given level with the minimal required concentration levels"""

        enc = True
        for ent,conc in state:
            e_id = self.rs.get_entity_id(ent)
            enc = And(enc, self.v[level][e_id] >= conc)

        # state_ids = self.rs.get_state_ids(state)
        #
        # for entity in state_ids:
        #     enc = And(enc, self.v[level][entity])

        return simplify(enc)
        

    def enc_state_with_blocking(self, level, prop):
        """Encodes the state at the given level with blocking certain concentrations"""

        required,blocked = prop

        enc = True
        for ent,conc in required:
                e_id = self.rs.get_entity_id(ent)
                enc = And(enc, self.v[level][e_id] >= conc)

        for ent,conc in blocked:
                e_id = self.rs.get_entity_id(ent)
                enc = And(enc, self.v[level][e_id] < conc)

        return simplify(enc)
        

    def decode_witness(self, max_level, print_model=False):

        m = self.solver.model()

        if print_model:
            print(m)

        for level in range(max_level+1):

            print("\n{: >70}".format("[ level=" + repr(level) + " ]"))

            print("  State: {", end=""),
            for var_id in range(len(self.v[level])):
                var_rep = repr(m[self.v[level][var_id]])
                if not var_rep.isdigit():
                    raise RuntimeError("unexpected: representation is not a positive integer")
                if int(var_rep) > 0:
                    print(" " + self.rs.get_entity_name(var_id) + "=" + var_rep, end="")
                # print(" " + repr(m[self.v[level][var_id]]), end="")
            print(" }")

            if level != max_level:
                print("  Context set: ", end="")
                print("{", end="")
                for var_id in range(len(self.v[level])):
                    var_rep = repr(m[self.v_ctx[level][var_id]])
                    if not var_rep.isdigit():
                        raise RuntimeError("unexpected: representation is not a positive integer")
                    if int(var_rep) > 0:
                        print(" " + self.rs.get_entity_name(var_id) + "=" + var_rep, end="")
                print(" }")
                
                
    def check_rsltl(self, formula, print_witness=True, print_time=True, print_mem=True, max_level=None):
        """Bounded Model Checking for rsLTL properties"""
        
        self.reset()
        
        print("[" + colour_str(C_BOLD, "i") + "] Running rsLTL bounded model checking")
        print("[" + colour_str(C_BOLD, "i") + "] Formula: " + str(formula))
        
        if print_time:
            # start = time()
            start = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        self.current_level = 0

        self.prepare_all_variables()
    
        self.solver.add(self.enc_concentration_levels_assertion(0))
    
        encoder = rsLTL_Encoder(self)
    
        while True:
            self.prepare_all_variables()
            self.solver.add(self.enc_concentration_levels_assertion(self.current_level+1))
        
            print("\n{:-^70}".format("[ Working at level=" + str(self.current_level) + " ]"))
            stdout.flush()

            # reachability test:
            self.solver.push()
            
            print("[" + colour_str(C_BOLD, "i") + "] Generating the formula encoding...")
            
            f = encoder.get_encoding(formula, self.current_level)
            ncalls = encoder.get_ncalls()
            
            print("[" + colour_str(C_BOLD, "i") + "] Cache hits: " + str(encoder.get_cache_hits()) + ", encode calls: " + str(ncalls[0]) + " (approx: " + str(ncalls[1]) + ")")
            print("[" + colour_str(C_BOLD, "i") + "] Adding the formula to the solver...")
            
            encoder.flush_cache()
            self.solver.add(f)
            
            print("[" + colour_str(C_BOLD, "i") + "] Adding the loops encoding...")
            self.solver.add(self.get_loop_encodings())
            
            result = self.solver.check()
            if result == sat:
                print("[" + colour_str(C_BOLD, "+") + "] " + colour_str(C_GREEN, "SAT at level=" + str(self.current_level)))
                if print_witness:
                    print("\n{:=^70}".format("[ WITNESS ]"))
                    self.decode_witness(self.current_level)
                break
            else:
                self.solver.pop()

            print("[" + colour_str(C_BOLD, "i") + "] Unrolling the transition relation")
            self.solver.add(self.enc_transition_relation(self.current_level))

            print("{:->70}".format("[ level=" + str(self.current_level) + " done ]"))
            self.current_level += 1

            if not max_level is None and self.current_level > max_level:
                print("Stopping at level=" + str(max_level))
                break

        if print_time:
            # stop = time()
            stop = resource.getrusage(resource.RUSAGE_SELF).ru_utime
            self.verification_time = stop-start
            print()
            print("\n[i] {: >60}".format(" Time: " + repr(self.verification_time) + " s"))
        
        if print_mem:
            print("[i] {: >60}".format(" Memory: " + repr(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024*1024)) + " MB"))
        
        
    def dummy_unroll(self, levels):
        """Unrolls the variables for testing purposes"""

        self.current_level = -1     
        for i in range(levels+1):
            self.prepare_all_variables()
            self.current_level += 1

        print(C_MARK_INFO + " Dummy Unrolling done.")
        
    
    def state_equality(self, level_A, level_B):
        """Encodes equality of two states at two different levels"""
        
        eq_enc = True
        
        for e_i in range(len(self.rs.background_set)):
            e_i_equality = self.v[level_A][e_i] == self.v[level_B][e_i]
            eq_enc = simplify(And(eq_enc, e_i_equality))

        eq_enc_ctxaut = self.ca_state[level_A] == self.ca_state[level_B]
        eq_enc = simplify(And(eq_enc, eq_enc_ctxaut))

        return eq_enc
        
    
    def get_loop_encodings(self):
        
        k = self.current_level
        loop_var = self.loop_position
        
        loop_enc = True
        
        """
        (loop_var == i) means that there is a loop taking back to the state (i-1)
        
        Therefore, the encoding starts at 1, not at 0.
        """
        
        for i in range(1,k+1):
            loop_enc = simplify(And(loop_enc, Implies( loop_var == i, self.state_equality(i-1, k) )))
        
        return loop_enc
        
        
    def check_reachability(self, state, print_witness=True, 
            print_time=True, print_mem=True, max_level=1000):
        """Main testing function"""

        self.reset()

        if print_time:
            # start = time()
            start = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        self.prepare_all_variables()
        self.solver.add(self.enc_init_state(0))
        self.current_level = 0

        self.prepare_all_variables()
        
        self.solver.add(self.enc_concentration_levels_assertion(0))
        
        while True:
            self.prepare_all_variables()
            self.solver.add(self.enc_concentration_levels_assertion(self.current_level+1))
            
            print("\n{:-^70}".format("[ Working at level=" + str(self.current_level) + " ]"))
            stdout.flush()

            # reachability test:
            print("[" + colour_str(C_BOLD, "i") + "] Adding the reachability test...")       
            self.solver.push()

            self.solver.add(self.enc_state_with_blocking(self.current_level,state))
                
            result = self.solver.check()
            if result == sat:
                print("[" + colour_str(C_BOLD, "+") + "] " + colour_str(C_GREEN, "SAT at level=" + str(self.current_level)))
                if print_witness:
                    print("\n{:=^70}".format("[ WITNESS ]"))
                    self.decode_witness(self.current_level)
                break
            else:
                self.solver.pop()

            print("[" + colour_str(C_BOLD, "i") + "] Unrolling the transition relation")
            self.solver.add(self.enc_transition_relation(self.current_level))

            print("{:->70}".format("[ level=" + str(self.current_level) + " done ]"))
            self.current_level += 1

            if self.current_level > max_level:
                print("Stopping at level=" + str(max_level))
                break

        if print_time:
            # stop = time()
            stop = resource.getrusage(resource.RUSAGE_SELF).ru_utime
            self.verification_time = stop-start
            print()
            print("\n[i] {: >60}".format(" Time: " + repr(self.verification_time) + " s"))
            
        if print_mem:
            print("[i] {: >60}".format(" Memory: " + repr(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024*1024)) + " MB"))
    
    
    def get_verification_time(self):
        return self.verification_time
    
    
    def show_encoding(self, state, print_witness=True, 
            print_time=False, print_mem=False, max_level=100):
        """Encoding debug function"""

        self.reset()

        self.prepare_all_variables()
        init_s = self.enc_init_state(0)
        print(init_s)
        self.solver.add(init_s)
        self.current_level = 0

        self.prepare_all_variables()
        
        while True:
            self.prepare_all_variables()

            print("-----[ Working at level=" + str(self.current_level) + " ]-----")
            stdout.flush()

            # reachability test:
            print("[i] Adding the reachability test...")       
            self.solver.push()

            s = self.enc_min_state(self.current_level,state)
            print("Test: ", s)
            
            self.solver.add(s)
                
            result = self.solver.check()
            if result == sat:
                print("\n[+] " + colour_str(C_RED, "SAT at level=" + str(self.current_level)))
                if print_witness:
                    self.decode_witness(self.current_level)
                break
            else:
                self.solver.pop()

            print("[i] Unrolling the transition relation")
            t = self.enc_transition_relation(self.current_level)
            print(t)
            self.solver.add(t)

            print("-----[ level=" + str(self.current_level) + " done ]")
            self.current_level += 1

            if self.current_level > max_level:
                print("Stopping at level=" + str(max_level))
                break
            else:
                x=input("Next level? ")
                x=x.lower()
                if not (x == "y" or x == "yes"):
                    break


# EOF