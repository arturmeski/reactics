from enum import Enum

LTL_form_type = Enum('LTL_form_type', 'proposition negation globally next until release')

class FormulaLTL(object):
    
    def __init__(self, type, L_oper = None, R_oper = None, proposition = ""):
        self.type = type
        self.left_operand = L_oper
        self.right_operand = R_oper
        self.proposition = proposition
    
    def __repr__(self):
        if self.type == LTL_form_type.proposition:
            return self.proposition
        if self.type == LTL_form_type.negation:
            return "NOT( " + repr(self.left_operand) + " )"
        if self.type == LTL_form_type.globally:
            return "G( " + repr(self.left_operand) + " )"
        if self.type == LTL_form_type.next:
            return "X( " + repr(self.left_operand) + " )"
        if self.type == LTL_form_type.until:
            return "( " + repr(self.left_operand) + " U " + repr(self.right_operand) + " )"
        if self.type == LTL_form_type.release:
            return "( " + repr(self.left_operand) + " R " + repr(self.right_operand) + " )"

    @classmethod
    def f_prop(cls, proposition_name):
        return cls(LTL_form_type.proposition, proposition = proposition_name)

    @classmethod
    def f_NOT(cls, arg):
        return cls(LTL_form_type.negation, L_oper = arg)

    @classmethod
    def f_X(cls, arg):
        return cls(LTL_form_type.next, L_oper = arg)

    @classmethod
    def f_G(cls, arg):
        return cls(LTL_form_type.globally, L_oper = arg)
    
    @classmethod
    def f_U(cls, arg_L, arg_R):
        return cls(LTL_form_type.until, L_oper = arg_L, R_oper = arg_R)

    @classmethod
    def f_R(cls, arg_L, arg_R):
        return cls(LTL_form_type.release, L_oper = arg_L, R_oper = arg_R)
    

x = FormulaLTL.f_NOT( FormulaLTL.f_X( FormulaLTL.f_prop("a") ) )

print(x)

        

