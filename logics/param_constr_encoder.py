from logics.param_constr import *
from z3 import And, Not, Or

class ParamConstr_Encoder(object):
    """Class for encoding parameter constraints"""
        
    def __init__(self, smt_checker):
        self.smt_checker = smt_checker
        self.rs = smt_checker.rs

        # self.v = None
        # self.v_ctx = None
        # self.loop_position = None
        
    def load_variables(self, var_rs, var_ctx, var_loop_pos):
        
        self.v = var_rs
        self.v_ctx = var_ctx
        self.loop_position = var_loop_pos
        
    def encode(self, param_constr):
        
        if not param_constr:
            raise RuntimeError("param_constr is None")

        if param_constr.f_type == ParamConstraint_oper.param_entity:
            return self.smt_checker.get_enc_param(param_constr.param.name, param_constr.entity)
            
        if param_constr.f_type == ParamConstraint_oper.true:
            return True
            
        if param_constr.f_type == ParamConstraint_oper.l_and:
            return And(self.encode(param_constr.left_operand), 
                self.encode(param_constr.right_operand))
            
        if param_constr.f_type == ParamConstraint_oper.l_or:
            return Or(self.encode(param_constr.left_operand), 
                self.encode(param_constr.right_operand))
            
        if param_constr.f_type == ParamConstraint_oper.l_not:
            return Not(self.encode(param_constr.left_operand))
            
        if param_constr.f_type == ParamConstraint_oper.lt:
            return self.encode(param_constr.left_operand) < int(param_constr.right_operand)
            
        if param_constr.f_type == ParamConstraint_oper.le:
            return self.encode(param_constr.left_operand) <= int(param_constr.right_operand)
            
        if param_constr.f_type == ParamConstraint_oper.eq:
            return self.encode(param_constr.left_operand) == int(param_constr.right_operand)
            
        if param_constr.f_type == ParamConstraint_oper.ge:
            return self.encode(param_constr.left_operand) >= int(param_constr.right_operand)
            
        if param_constr.f_type == ParamConstraint_oper.gt:
            return self.encode(param_constr.left_operand) > int(param_constr.right_operand)
            
        assert False, "Unsupported case {:s}".format(param_constr.f_type)
    
