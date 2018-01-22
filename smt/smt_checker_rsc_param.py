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
from logics import ParamConstr_Encoder

from rs.reaction_system_with_concentrations_param import ParameterObj, is_param

# def simplify(x):
#     return x

def z3_max(a, b):
    return If(a > b, a, b)

class SmtCheckerRSCParam(object):

    def __init__(self, rsca, optimise=False):
    
        rsca.sanity_check()

        if not rsca.is_concentr_and_param_compatible():
            raise RuntimeError("RS and CA with concentrations (and parameters) expected")
        
        self.rs = rsca.rs
        self.ca = rsca.ca
        
        self.optimise = optimise

        self.initialise()
    
    def initialise(self):
        """Initialises all the variables used by the checker"""

        ### "Currently" used variables (loaded from self.path_v...)
        self.v = None
        self.v_ctx = None
        self.ca_state = None
        
        # intermediate products:
        self.v_improd = None
        self.v_improd_for_entities = None
        
        ### Per-path variables
        self.path_v = dict()
        self.path_v_ctx = dict()
        self.path_ca_state = dict()
        
        # intermediate products:
        self.path_v_improd = dict()
        self.path_v_improd_for_entities = dict()
        
        # parameters:
        self.v_param = dict()

        self.next_level_to_encode = 0

        # this is probably not needed anymore:
        # self.producible_entities = self.rs.get_producible_entities()
        # self.improducible_entities = set(self.rs.get_state_ids(self.rs.background_set)) - self.producible_entities
        
        # WARNING: improd vs. improducible
        # there is some confusion related to the variables naming:
        # improd - intermediate products
        # improducible - entities that are never produces (there is no reaction that produces that entity)
        
        # TODO: number of loops == number of paths
        self.loop_position = None
        self.path_loop_position = dict()
        
        if self.optimise:
            self.solver = Optimize()
        else:
            self.solver = Solver() #For("QF_FD")

        self.verification_time = None
                
        self.prepare_param_variables()

    def reset(self):
        """Reinitialises the state of the checker"""
        
        self.initialise()
        
    def prepare_all_variables(self, num_of_paths):

        for path_idx in range(num_of_paths):
            self.prepare_all_path_variables(path_idx)
        self.next_level_to_encode += 1
        
    def prepare_all_path_variables(self, path_idx):
        """Prepares the variables for a given path index"""

        print_info("Preparing variables for path={:d} (level={:d})".format(path_idx, self.next_level_to_encode))
        
        self.prepare_state_variables(path_idx)
        self.prepare_context_variables(path_idx)
        self.prepare_intermediate_product_variables(path_idx)
        self.prepare_loop_position_variables(path_idx)
            
    def prepare_loop_position_variables(self, path_idx):
        """Prepares the variables for loop positions"""
        
        self.path_loop_position[path_idx] = Int("p{:d}_loop_pos".format(path_idx))
        
    def prepare_context_variables(self, path_idx):
        """Prepares all the context variables"""

        level = self.next_level_to_encode

        self.path_v_ctx.setdefault(path_idx, [])
        assert len(self.path_v_ctx[path_idx]) == level
        
        variables = []
        for entity in self.rs.background_set:
            new_var = Int("p{:d}C{:d}_{:s}".format(path_idx, level, entity))
            variables.append(new_var)

        self.path_v_ctx[path_idx].append(variables)

    def prepare_state_variables(self, path_idx):
        """Prepares all the state variables"""

        level = self.next_level_to_encode
        
        # RS vars
        self.path_v.setdefault(path_idx, [])
        assert len(self.path_v[path_idx]) == level

        variables = []
        for entity in self.rs.background_set:
            new_var = Int("p{:d}L{:d}_{:s}".format(path_idx, level, entity))
            variables.append(new_var)
        self.path_v[path_idx].append(variables)
        
        # Context automaton states:
        self.path_ca_state.setdefault(path_idx, [])
        assert len(self.path_ca_state[path_idx]) == level
        
        ca_state_var = Int("p{:d}CA{:d}_state".format(path_idx, level))
        self.path_ca_state[path_idx].append(ca_state_var)

    def prepare_intermediate_product_variables(self, path_idx):
        """
        Prepares the intermediate product variables
        carrying the individual concentration levels produced
        by the reactions.

        These variables are used later on to encode the final
        concentration levels for all the entities
        """

        level = self.next_level_to_encode

        self.path_v_improd.setdefault(path_idx, [])
        self.path_v_improd_for_entities.setdefault(path_idx, [])
        
        # assert len(self.path_v_improd[path_idx]) == level
        # assert len(self.path_v_improd_for_entities[path_idx]) == level

        if level < 1:
            #
            # If we are at level==0, we add a dummy "level"
            # to match the indices of of the successors
            # which are always at level+1.
            #
            self.path_v_improd[path_idx].append(None)
            self.path_v_improd_for_entities[path_idx].append(None)

        reactions_dict = dict()
        number_of_reactions = len(self.rs.reactions)

        all_entities_dict = dict()

        for reaction in self.rs.reactions:
            *_, products = reaction

            reaction_id = self.rs.reactions.index(reaction)

            entities_dict = dict()
            
            if is_param(products):

                for entity in self.rs.set_of_bgset_ids:
                    entity_name = self.rs.get_entity_name(entity)
                    new_var = Int("p{:d}L{:d}_ImProd_r{:d}_{:s}".format(path_idx, level, reaction_id, entity_name))
                    entities_dict[entity] = new_var

                    all_entities_dict.setdefault(entity, [])
                    all_entities_dict[entity].append(new_var)
                                        
            else:
            
                for entity, conc in products:
                    entity_name = self.rs.get_entity_name(entity)
                    new_var = Int("p{:d}L{:d}_ImProd_r{:d}_{:s}".format(path_idx, level, reaction_id, entity_name))
                    entities_dict[entity] = new_var

                    all_entities_dict.setdefault(entity, [])
                    all_entities_dict[entity].append(new_var)

            reactions_dict[reaction_id] = entities_dict
        
        self.path_v_improd[path_idx].append(reactions_dict)
        self.path_v_improd_for_entities[path_idx].append(all_entities_dict)
    
    def prepare_param_variables(self):
        """
        Prepares variables for parameters
        
        A parameter (it's valuation) is a subset of the background set,
        therefore we need separate variables for each element of the
        background set.
        """
        
        for param_name in self.rs.parameters.keys():

            # we start collecting bg-related vars for the given param
            vars_for_param = []

            for entity in self.rs.ordered_list_of_bgset_ids:
                new_var = Int("Pm{:s}_{:s}".format(param_name, self.rs.get_entity_name(entity)))
                vars_for_param.append(new_var)

            self.v_param[param_name] = vars_for_param

    def get_enc_param(self, param_name, entity_name):
        """
        Returns encoded param[entity_name]
        """
        entity_id = self.rs.get_entity_id(entity_name)
        return self.v_param[param_name][entity_id]
        
    def load_varset_for_path(self, path_idx):
        """
        Loads the the variables for the path with path_idx
        """
        self.v = self.path_v[path_idx]
        self.v_ctx = self.path_v_ctx[path_idx]
        self.ca_state = self.path_ca_state[path_idx]        
        self.v_improd = self.path_v_improd[path_idx]
        self.v_improd_for_entities = self.path_v_improd_for_entities[path_idx]
        self.loop_position = self.path_loop_position[path_idx]

    def enc_param_concentration_levels_assertion(self):
        """
        Assertions for the parameter variables
        """
        
        if len(self.v_param) == 0:
            return True
        
        enc_param_gz = True
        enc_non_empty = True
        
        for param_vars in self.v_param.values():
            
            enc_param_at_least_one = False
            for pvar in param_vars:
            
                # TODO: fixed upper limit: 100 (have a per-param setting for that)
                enc_param_gz = simplify(And(enc_param_gz, pvar >= 0, pvar < 100))
                enc_param_at_least_one = simplify(Or(enc_param_at_least_one, pvar > 0))
            
            enc_non_empty = simplify(And(enc_non_empty, enc_param_at_least_one))
            
        return simplify(And(enc_param_gz, enc_non_empty))
    
    def assert_param_optimisation(self):

        for param_vars in self.v_param.values():
            for pvar in param_vars:
                # self.solver.add_soft(pvar == 0)
                self.solver.minimize(pvar)
                                       
    def enc_concentration_levels_assertion(self, level, path_idx):
        """
        Encodes assertions that (some) variables need to be >=0
        
        We do not need to actually control all the variables,
        only those that can possibly go below 0.
        """

        print_info("Concentration level assertions for path={:d} (level={:d})".format(path_idx, level))
        
        enc_gz = True

        for e_i in self.rs.set_of_bgset_ids:
            var = self.path_v[path_idx][level][e_i]
            var_ctx = self.path_v_ctx[path_idx][level][e_i]
            e_max = self.rs.get_max_concentration_level(e_i)
            enc_gz = simplify(And(enc_gz, var >= 0, var_ctx >= 0, var <= e_max, var_ctx <= e_max))
            
            vars_per_reaction = self.path_v_improd_for_entities[path_idx][level + 1]
            if e_i in vars_per_reaction:
                for var_improd in vars_per_reaction[e_i]:
                    enc_gz = simplify(And(enc_gz, var_improd >= 0, var_improd <= e_max))
        
        return enc_gz
 
    def enc_init_state(self, level, path_idx):
        """Encodes the initial state at the given level"""

        rs_init_state_enc = True

        for v in self.path_v[path_idx][level]:
            # the initial concentration levels are zeroed
            rs_init_state_enc = simplify(And(rs_init_state_enc, v == 0))

        ca_init_state_enc = self.path_ca_state[path_idx][level] == self.ca.get_init_state_id()

        init_state_enc = simplify(And(rs_init_state_enc, ca_init_state_enc))

        return init_state_enc

    def enc_transition_relation(self, level, path_idx):
        return simplify(
            And(self.enc_rs_trans(level, path_idx),
                self.enc_automaton_trans(level, path_idx)))

    def enc_param_sanity_for_reactions(self):
        """R < I constraint (R n I = 0)"""

        rct_inh_constr = True

        for reactants, inhibitors, products in self.rs.reactions:

            if is_param(reactants) or is_param(inhibitors):
            
                # 1. R and I
                if is_param(reactants) and is_param(inhibitors):
                    rct_param_name = reactants.name
                    inh_param_name = inhibitors.name

                    for entity in self.rs.set_of_bgset_ids:
                        rct_inh_constr = And(rct_inh_constr, 
                            Implies(self.v_param[inh_param_name][entity] > 0, 
                                self.v_param[rct_param_name][entity] < self.v_param[inh_param_name][entity]))

            elif (not is_param(reactants)) and is_param(inhibitors):
                inh_param_name = inhibitors.name
                
                for entity, conc in reactants:
                    assert conc > 0, "Unexpected concentration level!"
                    rct_inh_constr = And(rct_inh_constr, 
                        Implies(self.v_param[inh_param_name][entity] > 0,
                            conc < self.v_param[inh_param_name][entity]))
                
            elif is_param(reactants) and (not is_param(inhibitors)):
                rct_param_name = reactants.name
                
                for entity, conc in inhibitors:
                    assert conc > 0, "Unexpected concentration level!"
                    rct_inh_constr = And(rct_inh_constr, self.v_param[rct_param_name][entity] < conc)

        return rct_inh_constr
                        

    def enc_single_reaction(self, level, path_idx, reaction):
        """
        Encodes a single reaction

        For encoding the products we use intermediate variables:

            * each reaction has its own product variables,

            * those are meant to be used to compute the MAX concentration

        """

        reactants, inhibitors, products = reaction

        # we need reaction_id to find the intermediate product variable
        reaction_id = self.rs.reactions.index(reaction)

        # ** REACTANTS *******************************************
        enc_reactants = True
        if is_param(reactants):
            param_name = reactants.name
            for entity in self.rs.set_of_bgset_ids:
                enc_reactants = And(enc_reactants, Or(
                    self.v_param[param_name][entity] == 0,
                    self.path_v[path_idx][level][entity] >= self.v_param[param_name][entity], 
                    self.path_v_ctx[path_idx][level][entity] >= self.v_param[param_name][entity]))
        else:
            for entity, conc in reactants:
                enc_reactants = And(enc_reactants, Or(
                    self.path_v[path_idx][level][entity] >= conc, 
                    self.path_v_ctx[path_idx][level][entity] >= conc))

        # ** INHIBITORS ******************************************
        enc_inhibitors = True
        if is_param(inhibitors):
            param_name = inhibitors.name
            for entity in self.rs.set_of_bgset_ids:
                enc_inhibitors = And(enc_inhibitors, Or(
                    self.v_param[param_name][entity] == 0,
                    And(
                        self.path_v[path_idx][level][entity] < self.v_param[param_name][entity], 
                        self.path_v_ctx[path_idx][level][entity] < self.v_param[param_name][entity])))
        else:
            for entity, conc in inhibitors:
                enc_inhibitors = And(enc_inhibitors, And(
                    self.path_v[path_idx][level][entity] < conc, 
                    self.path_v_ctx[path_idx][level][entity] < conc))

        # ** PRODUCTS *******************************************
        enc_products = True
        if is_param(products):
            param_name = products.name
            for entity in self.rs.set_of_bgset_ids:
                enc_products = simplify(And(enc_products,
                    self.path_v_improd[path_idx][level + 1][reaction_id][entity] == self.v_param[param_name][entity]))
        else:
            for entity, conc in products:
                enc_products = simplify(And(enc_products, 
                    self.path_v_improd[path_idx][level + 1][reaction_id][entity] == conc))

        # Nothing is produced (when the reaction is disabled)
        enc_no_prod = True
        if is_param(products):
            for entity in self.rs.set_of_bgset_ids:
                enc_no_prod = And(enc_no_prod,
                    self.path_v_improd[path_idx][level + 1][reaction_id][entity] == 0)
        else:
            for entity, _ in products:
                enc_no_prod = simplify(And(enc_no_prod, 
                    self.path_v_improd[path_idx][level + 1][reaction_id][entity] == 0))

        
        #
        # (R and I) iff P
        #
        enc_enabled = And(enc_reactants, enc_inhibitors) == enc_products
        
        #
        # ~(R and I) iff P_zero
        #
        enc_not_enabled = Not(And(enc_reactants, enc_inhibitors)) == enc_no_prod
        
        enc_reaction = And(enc_enabled, enc_not_enabled)

        return enc_reaction

    def enc_general_reaction_enabledness(self, level, path_idx):
        """
        General enabledness condition for reactions
        
        The necessary condition for a reaction to be enabled is
        that the state is not empty, i.e., at least one entity
        is present in the current state.
        
        This condition must be used when there are parametric reactions
        because parameters could have all the entities set to zero and
        that immediately allows for all the conditions on the reactants
        to be fulfilled: (entity <= param) -> (0 <= 0)
        """
        
        enc_cond = False
        for entity in self.rs.set_of_bgset_ids:
            enc_cond = simplify(Or(enc_cond, self.path_v[path_idx][level][entity] > 0, self.path_v_ctx[path_idx][level][entity] > 0))

        return enc_cond

    def enc_rs_trans(self, level, path_idx):
        """Encodes the transition relation"""

        #
        # IMPORTANT NOTE
        #
        # We need to make sure we do something about the UNUSED ENTITIES
        # that is, those that are never produced.
        #
        # They should have concentration levels set to 0.
        #
        # That needs to happen automatically (in the MAX encoding) -- for the parametric 
        # case it makes no sense to identify the entities that are never produced, unless 
        # we have no parameters as products (special case, so that could be an 
        # optimisation)
        #

        enc_trans = True

        for reaction in self.rs.reactions:
            enc_reaction = self.enc_single_reaction(level, path_idx, reaction)
            enc_trans = simplify(And(enc_trans, enc_reaction))

        # Next we encode the MAX concentration values: 
        # we collect those from the intermediate product variables

        enc_max_prod = True

        # Save all the intermediate product variables for a given level:
        #
        # - Intermediate products of (level+1) correspond to the next level
        #
        #   {reactants & inhibitors}[level] 
        #       => 
        #   {improd}[level+1] 
        #       => 
        #   {products}[level+1]
        #
        current_v_improd_for_entities = self.path_v_improd_for_entities[path_idx][level + 1]
        for entity in self.rs.set_of_bgset_ids:
            per_reaction_vars = current_v_improd_for_entities.get(entity, [])
            enc_max_prod = simplify(
                And(enc_max_prod, self.path_v[path_idx][level + 1][entity] == self.enc_max(per_reaction_vars)))
        
        # make sure at least one entity is >0
        enc_general_cond = self.enc_general_reaction_enabledness(level, path_idx)

        enc_trans_with_max = simplify(And(enc_general_cond, enc_max_prod, enc_trans))

        # print(enc_trans_with_max)

        return enc_trans_with_max

    def enc_max(self, elements):

        enc = None
        
        if elements == []:
            enc = 0

        elif len(elements) == 1:
            enc = z3_max(0, elements[0])

        elif len(elements) > 1:

            enc = 0
            for i in range(len(elements) - 1):
                enc = z3_max(enc, z3_max(elements[i], elements[i + 1]))

        return enc
    
    def enc_automaton_trans(self, level, path_idx):
        """Encodes the transition relation for the context automaton"""
        
        enc_trans = False
    
        for src,ctx,dst in self.ca.transitions:
                src_enc = self.path_ca_state[path_idx][level] == src
                dst_enc = self.path_ca_state[path_idx][level+1] == dst
                
                all_ent = set(range(len(self.rs.background_set)))
                
                incl_ctx = set([e for e,c in ctx])
                excl_ctx = all_ent - incl_ctx
                
                ctx_enc = True
                
                for e,c in ctx:
                    ctx_enc = simplify(And(ctx_enc, self.path_v_ctx[path_idx][level][e] == c))
                
                for e in excl_ctx:
                    ctx_enc = simplify(And(ctx_enc, self.path_v_ctx[path_idx][level][e] == 0))
                
                cur_trans = simplify(And(src_enc, ctx_enc, dst_enc))
                enc_trans = simplify(Or(enc_trans, cur_trans))
        
        return enc_trans

    def enc_exact_state(self, level, state):
        """Encodes the state at the given level with the exact concentration values"""

        raise RuntimeError("Should not be used with RSC")

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

    def decode_witness(self, max_level, path_idx, print_model=False):
        """
        Decodes the witness
        
        Also decodes the parameters
        """

        m = self.solver.model()

        if print_model:
            print(m)

        for level in range(max_level + 1):

            print("\n{: >70}".format("[ level=" + repr(level) + " ]"))

            print("  State: {", end=""),
            for var_id in range(len(self.path_v[path_idx][level])):
                var_rep = repr(m[self.path_v[path_idx][level][var_id]])
                if not var_rep.isdigit():
                    raise RuntimeError(
                        "unexpected: representation is not a positive integer")
                if int(var_rep) > 0:
                    print(
                        " " + self.rs.get_entity_name(var_id) + "=" + var_rep,
                        end="")
                # print(" " + repr(m[self.v[level][var_id]]), end="")
            print(" }")

            if level != max_level:
                print("  Context set: ", end="")
                print("{", end="")
                for var_id in range(len(self.path_v[path_idx][level])):
                    var_rep = repr(m[self.path_v_ctx[path_idx][level][var_id]])
                    if not var_rep.isdigit():
                        raise RuntimeError(
                            "unexpected: representation is not a positive integer")
                    if int(var_rep) > 0:
                        print(
                            " " + self.rs.get_entity_name(var_id) + "=" + var_rep,
                            end="")
                print(" }")
        
        print()
        
    def get_enc_formulae(self, encoder, formulae_list):
        enc_form = []
        for formula in formulae_list:
            
            path_idx = formulae_list.index(formula)
            
            print_info("Generating the encoding for {:s} ({:d} of {:d})".format(
                str(formula), path_idx+1, len(formulae_list)))

            encoder.load_variables(
                var_rs=self.path_v[path_idx],
                var_ctx=self.path_v_ctx[path_idx],
                var_loop_pos=self.path_loop_position[path_idx])
                
            enc_form.append(encoder.get_encoding(formula, self.current_level))
            ncalls = encoder.get_ncalls()

            print_info("Cache hits: {:d}, encode calls: {:d} (approx: {:d})".format(
                    encoder.get_cache_hits(), ncalls[0], ncalls[1]))

            encoder.flush_cache()
            
        return enc_form
        
    def print_witness(self, formulae_list):
    
        for formula in formulae_list:
            path_idx = formulae_list.index(formula)
            print("\n{:=^70}".format("[ WITNESS ]"))
            print("\n  Witness for: {:s}".format(str(formula)))
            self.decode_witness(self.current_level, path_idx)
        
        self.print_parameter_valuations()   
    
    def print_parameter_valuations(self):

        m = self.solver.model()

        print("\n  Parameters:\n")
        for param_name in sorted(self.rs.parameters.keys()):
            print("{: >6}: ".format(param_name), end="")
            print("{", end="")
            
            params = self.v_param[param_name]
            
            for entity in self.rs.set_of_bgset_ids:
                var_rep = repr(m[params[entity]])
                if not var_rep.isdigit():
                    raise RuntimeError(
                        "unexpected: representation is not a positive integer")
                if int(var_rep) > 0:
                    print(
                        " " + str(self.rs.get_entity_name(entity)) + "=" + str(var_rep),
                        end="")
            print(" }")
    
        print()
        
    def enc_concentration_levels_assertions_for_paths(self, level, num_of_paths):
    
        additional_assertions = []
        for path_idx in range(num_of_paths):
            additional_assertions.append(self.enc_concentration_levels_assertion(level, path_idx))
        additional_assertions.append(self.enc_param_concentration_levels_assertion())
        
        return additional_assertions
    
    def enc_transition_relation_for_paths(self, level, num_of_paths):
        enc_trans = []
        for path_idx in range(num_of_paths):
            enc_trans.append(self.enc_transition_relation(level, path_idx))
        return enc_trans
        
    def print_level(self):
        print(
            "{:->70}".format("[ level=" + str(self.current_level) + " done ]"))
    
    def check_rsltl(
            self, formulae_list, 
            print_witness=True, 
            print_time=True, print_mem=True,
            max_level=None, cont_if_sat=False,
            param_constr=None):
        """
        Bounded Model Checking for rsLTL properties
            
            * print_witness   -- prints the decoded witness
            * print_time      -- prints the time consumed
            * print_mem       -- prints the memory consumed
            * max_level       -- if not None, the methods 
                                 stops at the specified level
            * cont_if_sat     -- if True, then the method
                                 continues up until max_level is
                                 reached (even if sat found)
            * param_constr    -- constraints on parameters
        """
            
        if not isinstance(formulae_list, (list, tuple)):
            print_error("Expected a list of formulae")
        
        #print_info("Parameter constraint: {:s}".format(str(param_constr)))
        print_info("Parameter constraint defined")


        self.reset()

        num_of_paths = len(formulae_list)
        
        # formula = formulae[0]

        print_info("Running rsLTL bounded model checking")
        print_info("Tested formulae:")
        for form in formulae_list:
            print_info(" "*4 + str(form))

        print_info("INITIALISING...")

        if print_time:
            start_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        self.prepare_all_variables(num_of_paths)
        
        self.load_varset_for_path(0)
        
        # initial states for all the paths
        initial_states = []
        for path_idx in range(num_of_paths):
            initial_states.append(self.enc_init_state(0, path_idx))
        self.solver_add(initial_states)
        
        self.current_level = 0

        # self.prepare_all_variables(num_of_paths)

        # assertions for all the paths and parameters
        self.solver_add(self.enc_concentration_levels_assertions_for_paths(0, num_of_paths))
        self.solver_add(self.enc_param_concentration_levels_assertion())
        self.solver_add(self.enc_param_sanity_for_reactions())

        encoder = rsLTL_Encoder(self)
        
        if param_constr:
            param_contr_encoder = ParamConstr_Encoder(self)
            enc_param_constr = param_contr_encoder.encode(param_constr)
            self.solver_add(enc_param_constr)

        if self.optimise:
            self.assert_param_optimisation()

        print_info("STARTING TO ITERATE...")
        
        while True:
            
            print(
                "\n{:-^70}".format("[ Working at level=" + str(self.current_level) + " ]"))
            # stdout.flush()

            # reachability test:
            self.solver.push()

            # Encoding all the formulae
            enc_form = self.get_enc_formulae(encoder, formulae_list)
            print_info("Adding the formulae to the solver...")
            self.solver_add(enc_form)

            # Loops encoding
            print_info("Adding the encoding for the loops...")
            self.solver_add(self.get_loop_encodings())

            # if self.optimise:
            #     self.assert_param_optimisation()

            print_info("Testing satisfiability...")
            result = self.solver.check()
            if result == sat:
                print_positive(green_str(
                        "SAT at level={:d}".format(self.current_level)))
                # print(self.solver.model())
                if print_witness:
                    self.print_witness(formulae_list)
                if not cont_if_sat:
                    break
            else:
                print_info("UNSAT")
                self.solver.pop()

            if not max_level is None and self.current_level > max_level:
                print_info("As requested, stopping at level=" + str(max_level))
                break

            self.prepare_all_variables(num_of_paths)
            
            # assertions for all the paths
            self.solver_add(self.enc_concentration_levels_assertions_for_paths(self.current_level + 1, num_of_paths))

            print_info("Unrolling the transition relation")
            self.solver_add(self.enc_transition_relation_for_paths(self.current_level, num_of_paths))

            self.print_level()

            self.current_level += 1

        if print_time:
            self.print_time(start_time)
        if print_mem:
            self.print_mem()

    def print_time(self, start):
        stop = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        self.verification_time = stop - start
        print()
        print_info("{: >60}".format(
                " Time: " + repr(self.verification_time) + " s"))
    
    def print_mem(self):
        print_info(
            "{: >60}".format(
                " Memory: " +
                repr(
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss /
                    (1024 * 1024)) + " MB"))
    
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
    
    def solver_add(self, expression):
        """
        This is a solver.add() wrapper
        """
    
        if expression == True:
            return
    
        if expression == False:
            raise RuntimeError("Trying to assert False.")
        
        self.solver.add(expression)

    def check_reachability(self, state, print_witness=True, 
            print_time=True, print_mem=True, max_level=1000):
        """Main testing function"""

        self.reset()

        if print_time:
            # start = time()
            start = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        self.prepare_all_variables()
        self.solver_add(self.enc_init_state(0))
        self.current_level = 0

        self.prepare_all_variables()
        
        self.solver_add(self.enc_concentration_levels_assertion(0))
        
        while True:
            self.prepare_all_variables()
            self.solver_add(self.enc_concentration_levels_assertion(self.current_level+1))
            
            print("\n{:-^70}".format("[ Working at level=" + str(self.current_level) + " ]"))
            stdout.flush()

            # reachability test:
            print("[" + colour_str(C_BOLD, "i") + "] Adding the reachability test...")       
            self.solver.push()

            self.solver_add(self.enc_state_with_blocking(self.current_level,state))
                
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
            self.solver_add(self.enc_transition_relation(self.current_level))

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
        self.solver_add(init_s)
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
            
            self.solver_add(s)

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
            self.solver_add(t)

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
