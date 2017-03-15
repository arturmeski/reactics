from logics.rsltl import *

def simplify(x):
    return x

class rsLTL_Encoder(object):
    """Class for encoding rsLTL formulae for a given smt_checker instance"""
        
    def __init__(self, smt_checker):
        self.smt_checker = smt_checker
        self.v = smt_checker.v
        self.v_ctx = smt_checker.v_ctx
        self.rs = smt_checker.rs
        self.loop_position = smt_checker.loop_position
        
        self.init_ncalls()
        
    def init_ncalls(self):
        self.ncalls_encode = 0
        self.ncalls_encode_approx = 0
        
    def get_ncalls(self):
        return (self.ncalls_encode, self.ncalls_encode_approx)
        
    def encode_bag(self, bag_formula, level, context=False):

        if not bag_formula:
            raise RuntimeError("bag_formula is None")

        if bag_formula.f_type == BagDesc_oper.entity:
            entity_id = self.rs.get_entity_id(bag_formula.entity)
            if context:
                return self.v_ctx[level][entity_id]
            else:
                return self.v[level][entity_id]
            
        if bag_formula.f_type == BagDesc_oper.true:
            return True
            
        if bag_formula.f_type == BagDesc_oper.l_and:
            return And(self.encode_bag(bag_formula.left_operand, level, context), 
                self.encode_bag(bag_formula.right_operand, level, context))
            
        if bag_formula.f_type == BagDesc_oper.l_or:
            return Or(self.encode_bag(bag_formula.left_operand, level, context), 
                self.encode_bag(bag_formula.right_operand, level, context))
            
        if bag_formula.f_type == BagDesc_oper.l_not:
            return Not(self.encode_bag(bag_formula.left_operand, level, context))
            
        if bag_formula.f_type == BagDesc_oper.lt:
            return self.encode_bag(bag_formula.left_operand, level, context) < int(bag_formula.right_operand)
            
        if bag_formula.f_type == BagDesc_oper.le:
            return self.encode_bag(bag_formula.left_operand, level, context) <= int(bag_formula.right_operand)
            
        if bag_formula.f_type == BagDesc_oper.eq:
            return self.encode_bag(bag_formula.left_operand, level, context) == int(bag_formula.right_operand)
            
        if bag_formula.f_type == BagDesc_oper.ge:
            return self.encode_bag(bag_formula.left_operand, level, context) >= int(bag_formula.right_operand)
            
        if bag_formula.f_type == BagDesc_oper.gt:
            return self.encode_bag(bag_formula.left_operand, level, context) > int(bag_formula.right_operand)
    
    def encode_bag_state(self, bag_formula, level):
        return self.encode_bag(bag_formula, level)
        
    def encode_bag_ctx(self, bag_formula, level):
        return self.encode_bag(bag_formula, level, context=True)
      
    def encode(self, formula, level, bound):
        
        self.ncalls_encode += 1
        
        if not isinstance(formula, Formula_rsLTL):
            raise NotImplementedError("Unsupported formula type: " + str(type(formula)))
        
        if level > bound:
            raise RuntimeError("level > bound. Unexpected behaviour. The encoding does not support levels higher than a bound.")
    
        if formula.f_type == rsLTL_form_type.bag:
            return self.encode_bag_state(formula.bag_descr, level)

        elif formula.f_type == rsLTL_form_type.l_not:
            subform = formula.left_operand
            if subform.is_bag:
                return Not(self.encode_bag_state(subform, level))
            else:
                raise RuntimeError("Negation can be applied to bags only")
        
        elif formula.f_type == rsLTL_form_type.l_and:
            return And(
                    self.encode(formula.left_operand, level, bound), 
                    self.encode(formula.right_operand, level, bound)
            )

        elif formula.f_type == rsLTL_form_type.l_or:
            return Or(
                    self.encode(formula.left_operand, level, bound), 
                    self.encode(formula.right_operand, level, bound)
            )

        elif formula.f_type == rsLTL_form_type.l_implies:
            return Implies(
                    self.encode(formula.left_operand, level, bound), 
                    self.encode(formula.right_operand, level, bound)
            )
            
        elif formula.f_type == rsLTL_form_type.t_next:
            if level < bound:
                enc = And(
                        self.encode(formula.left_operand, level + 1, bound), 
                        self.encode_bag_ctx(formula.sub_operand, level)
                )
            else: 
                # level == bound
                enc = False
                for loop_level in range(1, bound+1):
                    enc = Or(enc, And(self.loop_position == loop_level, 
                        self.encode(formula.left_operand, loop_level, bound)))
                enc = And(enc, self.encode_bag_ctx(formula.sub_operand, level))
                enc = simplify(enc)
                
            return enc 

        elif formula.f_type == rsLTL_form_type.t_globally:
            if level < bound:
                enc = And(
                        self.encode(formula.left_operand, level, bound),
                        self.encode_bag_ctx(formula.sub_operand, level),
                        self.encode(formula, level + 1, bound)
                )
            else:
                # level == bound
                enc_loops = False
                for loop_level in range(1, bound+1):
                    enc_loops = Or(enc_loops, 
                        And(
                            self.loop_position == loop_level,
                            self.encode_approx(formula, loop_level, bound),
                        )
                    )
                enc = And(
                    self.encode(formula.left_operand, bound, bound),
                    enc_loops, 
                    self.encode_bag_ctx(formula.sub_operand, level)
                )
                enc = simplify(enc)  

            return enc

        elif formula.f_type == rsLTL_form_type.t_finally:
            if level < bound:
                enc = Or(
                        self.encode(formula.left_operand, level, bound),
                        And(
                            self.encode_bag_ctx(formula.sub_operand, level),
                            self.encode(formula, level + 1, bound)
                        )
                    )
            else:
                # level == bound
                enc_loops = False
                for loop_level in range(1, bound+1):
                    enc_loops = Or(enc_loops, 
                            And(
                                self.loop_position == loop_level,
                                self.encode_approx(formula, loop_level, bound),
                            )   
                        )
                    #print(enc)
                enc = Or(self.encode(formula.left_operand, bound, bound), 
                        And(
                            enc_loops, 
                            self.encode_bag_ctx(formula.sub_operand, level)
                        )
                    )
                
                enc = simplify(enc)

            return enc

        elif formula.f_type == rsLTL_form_type.t_until:
            if level < bound:
                inner_enc = self.encode(formula, level + 1, bound)
            else: 
                # level == bound
                inner_enc = False
                for loop_level in range(1, bound+1):
                    inner_enc = Or(inner_enc, 
                            And(
                                self.loop_position == loop_level, 
                                self.encode_approx(formula, loop_level, bound)
                            )
                        )

            enc = Or(
                    self.encode(formula.right_operand, level, bound), 
                    And(
                        self.encode(formula.left_operand, level, bound),
                        inner_enc,
                        self.encode_bag_ctx(formula.sub_operand, level)
                    )
                )
                                
            return enc
            
        elif formula.f_type == rsLTL_form_type.t_release:
            if level < bound:
                inner_enc = self.encode(formula, level + 1, bound)
            else: 
                # level == bound
                inner_enc = False
                for loop_level in range(1, bound+1):
                    inner_enc = Or(inner_enc, 
                            And(
                                self.loop_position == loop_level, 
                                self.encode_approx(formula, loop_level, bound)
                            )
                        )
                
            enc = And(
                    self.encode(formula.right_operand, level, bound), 
                    Or(
                        self.encode(formula.left_operand, level, bound),
                        And(
                            inner_enc,
                            self.encode_bag_ctx(formula.sub_operand, level)
                        )
                    )
                )

            return enc
        
        else:
            raise NotImplementedError("Unsupported operator")

    def encode_approx(self, formula, level, bound):
        """Provides the approximation-encoding
        
        Used by encode()
        """
        
        self.ncalls_encode_approx += 1
        
        if formula.f_type == rsLTL_form_type.t_until:
            if level < bound:
                enc = Or(
                        self.encode(formula.right_operand, level, bound), 
                        And(
                            self.encode(formula.left_operand, level, bound),
                            self.encode_approx(formula, level + 1, bound),
                            self.encode_bag_ctx(formula.sub_operand, level)
                        )
                    )
            else: 
                # level == bound
                enc = self.encode(formula.right_operand, bound, bound)
        
            return enc
    
        elif formula.f_type == rsLTL_form_type.t_release:
            if level < bound:
                enc = And(
                        self.encode(formula.right_operand, level, bound), 
                        Or(
                            self.encode(formula.left_operand, level, bound),
                            And(
                                self.encode_approx(formula, level + 1, bound),
                                self.encode_bag_ctx(formula.sub_operand, level)
                            )
                        )
                    )
            else: 
                # level == bound
                enc = self.encode(formula.right_operand, bound, bound)
        
            return enc

        elif formula.f_type == rsLTL_form_type.t_globally:
            if level < bound:
                enc = And(
                        self.encode(formula.left_operand, level, bound),
                        self.encode_bag_ctx(formula.sub_operand, level),
                        self.encode_approx(formula, level + 1, bound)
                    )
            else:
                # level == bound
                enc = self.encode(formula.left_operand, bound, bound)

            return enc

        elif formula.f_type == rsLTL_form_type.t_finally:
            if level < bound:
                enc = Or(
                        self.encode(formula.left_operand, level, bound),
                        And(
                            self.encode_bag_ctx(formula.sub_operand, level),
                            self.encode_approx(formula, level + 1, bound)
                        )
                    )
            else:
                # level == bound
                enc = self.encode(formula.left_operand, bound, bound)

            return enc        
        

        else:
            raise NotImplementedError("Unsupported operator in approximation encoding")

