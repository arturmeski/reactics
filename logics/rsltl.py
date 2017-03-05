from z3 import *
from enum import Enum

rsLTL_form_type = Enum('rsLTL_form_type', 'bag l_and l_or l_not globally next until release')
BagDesc_oper = Enum('BagDesc_oper', 'entity true l_and l_or l_not lt le eq ge gt')

class BagDescription(object):
    def __init__(self, f_type, L_oper = None, R_oper = None, entity = ""):
        self.f_type = f_type
        self.left_operand = L_oper
        self.right_operand = R_oper
        self.entity = entity
        
    def __repr__(self):
        if self.f_type == BagDesc_oper.entity:
            return self.entity
        if self.f_type == BagDesc_oper.true:
            return "TRUE"
        if self.f_type == BagDesc_oper.l_and:
            return "( " + repr(self.left_operand) + " & " + repr(self.right_operand) + " )"
        if self.f_type == BagDesc_oper.l_or:
            return "( " + repr(self.left_operand) + " | " + repr(self.right_operand) + " )"
        if self.f_type == BagDesc_oper.l_not:
            return "~" + repr(self.left_operand)
        if self.f_type == BagDesc_oper.lt:
            return repr(self.left_operand) + " < " + repr(self.right_operand)
        if self.f_type == BagDesc_oper.le:
            return repr(self.left_operand) + " <= " + repr(self.right_operand)
        if self.f_type == BagDesc_oper.eq:
            return repr(self.left_operand) + " == " + repr(self.right_operand)
        if self.f_type == BagDesc_oper.ge:
            return repr(self.left_operand) + " >= " + repr(self.right_operand)
        if self.f_type == BagDesc_oper.gt:
            return repr(self.left_operand) + " > " + repr(self.right_operand)
            
    def sanity_check(self):
        """Checks if the right operands for the relations are integers"""
        
        # TODO
        
        pass

    @classmethod
    def f_entity(cls, entity_name):
        return cls(BagDesc_oper.entity, entity = entity_name)
        
    @classmethod
    def f_TRUE(cls):
        return cls(BagDesc_oper.true)
        
    def __lt__(self, other):
        return BagDescription(BagDesc_oper.lt, L_oper = self, R_oper = other)
        
    def __le__(self, other):
        return BagDescription(BagDesc_oper.le, L_oper = self, R_oper = other)
        
    def __eq__(self, other):
        return BagDescription(BagDesc_oper.eq, L_oper = self, R_oper = other)
    
    def __ge__(self, other):
        return BagDescription(BagDesc_oper.ge, L_oper = self, R_oper = other)
    
    def __gt__(self, other):
        return BagDescription(BagDesc_oper.gt, L_oper = self, R_oper = other)
        
    def __and__(self, other):
        return BagDescription(BagDesc_oper.l_and, L_oper = self, R_oper = other)
    
    def __or__(self, other):
        return BagDescription(BagDesc_oper.l_or, L_oper = self, R_oper = other)
    
    def __invert__(self):
        return BagDescription(BagDesc_oper.l_not, L_oper = self)

class Formula_rsLTL(object):
    
    def __init__(self, f_type, L_oper = None, R_oper = None, sub_oper = None, bag = None):
        self.f_type = f_type
        self.left_operand = L_oper
        self.right_operand = R_oper
        self.sub_operand = sub_oper
        self.bag_descr = bag
    
    def __repr__(self):
        if self.f_type == rsLTL_form_type.bag:
            return repr(self.bag_descr)
        if self.f_type == rsLTL_form_type.l_not:
            return "~( " + repr(self.left_operand) + " )"
        if self.f_type == rsLTL_form_type.globally:
            return "G[" + repr(self.sub_operand) + "]( " + repr(self.left_operand) + " )"
        if self.f_type == rsLTL_form_type.next:
            return "X[" + repr(self.sub_operand) + "]( " + repr(self.left_operand) + " )"
        if self.f_type == rsLTL_form_type.l_and:
            return "( " + repr(self.left_operand) + " & " + repr(self.right_operand) + " )"
        if self.f_type == rsLTL_form_type.l_or:
            return "( " + repr(self.left_operand) + " | " + repr(self.right_operand) + " )"
        if self.f_type == rsLTL_form_type.until:
            return "( " + repr(self.left_operand) + " U[" + repr(self.sub_operand) + "]" + repr(self.right_operand) + " )"
        if self.f_type == rsLTL_form_type.release:
            return "( " + repr(self.left_operand) + " R[" + repr(self.sub_operand) + "]" + repr(self.right_operand) + " )"

    @classmethod
    def f_bag(cls, bag_descr):
        return cls(rsLTL_form_type.bag, bag = bag_descr)

    @classmethod
    def f_X(cls, sub, arg):
        return cls(rsLTL_form_type.next, L_oper = arg, sub_oper = sub)

    @classmethod
    def f_G(cls, sub, arg):
        return cls(rsLTL_form_type.globally, L_oper = arg, sub_oper = sub)
    
    @classmethod
    def f_U(cls, sub, arg_L, arg_R):
        return cls(rsLTL_form_type.until, L_oper = arg_L, R_oper = arg_R, sub_oper = sub)

    @classmethod
    def f_R(cls, sub, arg_L, arg_R):
        return cls(rsLTL_form_type.release, L_oper = arg_L, R_oper = arg_R, sub_oper = sub)
        
    def __and__(self, other):
        return FormulaLTL(rsLTL_form_type.l_and, L_oper = self, R_oper = other)
    
    def __or__(self, other):
        return FormulaLTL(rsLTL_form_type.l_or, L_oper = self, R_oper = other)
    
    def __invert__(self):
        return FormulaLTL(rsLTL_form_type.l_not, L_oper = self)

#x = ~( FormulaLTL.f_X(BagDescription.f_TRUE(), FormulaLTL.f_bag( ~((BagDescription.f_entity("ent1") == 3) | (BagDescription.f_entity("ent2") < 3)) ) ) ) & FormulaLTL.f_X(BagDescription.f_TRUE(), FormulaLTL.f_bag( ~((BagDescription.f_entity("ent3") == 1) ) ) ) 
#print(x)

class Encoder_rsLTL(object):
    """Class for encoding rsLTL formulae for a given smt_checker instance"""
        
    def __init__(self, smt_checker):
        self.smt_checker = smt_checker
        self.v = smt_checker.v
        self.v_ctx = smt_checker.v_ctx
        self.rs = smt_checker.rs
        
    def encode_bag(self, bag_formula, level, context=False):
        if bag_formula.f_type == BagDesc_oper.entity:
            entity_id = self.rs.get_entity_id(self.entity)
            if context:
                return self.v_ctx[level][entity_id]
            else:
                return self.v[level][entity_id]
            
        if bag_formula.f_type == BagDesc_oper.true:
            return True
            
        if bag_formula.f_type == BagDesc_oper.l_and:
            return And(self.encode_bag(bag_formula.left_operand, level, context), self.encode_bag(bag_formula.left_.right_operand, level, context))
            
        if bag_formula.f_type == BagDesc_oper.l_or:
            return Or(self.encode_bag(bag_formula.left_operand, level, context), self.encode_bag(bag_formula.right_operand, level, context))
            
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
        
    def encode(self, formula, position, bound):
    
        if formula.f_type == rsLTL_form_type.bag:
            return self.encode_bag()

        
            
        # if formula.f_type == rsLTL_form_type.l_not:
        #     return "~( " + repr(formula.left_operand) + " )"
        #
        # if formula.f_type == rsLTL_form_type.globally:
        #     return "G[" + repr(self.sub_operand) + "]( " + repr(formula.left_operand) + " )"
        #
        # if formula.f_type == rsLTL_form_type.next:
        #     return "X[" + repr(self.sub_operand) + "]( " + repr(formula.left_operand) + " )"
        #
        # if formula.f_type == rsLTL_form_type.l_and:
        #     return "( " + repr(formula.left_operand) + " & " + repr(formula.right_operand) + " )"
        #
        # if formula.f_type == rsLTL_form_type.l_or:
        #     return "( " + repr(formula.left_operand) + " | " + repr(formula.right_operand) + " )"
        #
        # if formula.f_type == rsLTL_form_type.until:
        #     return "( " + repr(formula.right_operand) + " U[" + repr(self.sub_operand) + "]" + repr(formula.right_operand) + " )"
        #
        # if formula.left_ == rsLTL_form_type.release:
        #     return "( " + repr(formula.left_operand) + " R[" + repr(self.sub_operand) + "]" + repr(formula.right_operand) + " )"
        
        
    
