from enum import Enum
ParamConstraint_oper = Enum(
    'ParamConstraint_oper', 'param_entity true l_and l_or l_not lt le eq ge gt')


class ParamConstraint(object):

    def __init__(self, f_type, L_oper=None, R_oper=None, param=None, entity=""):
        self.f_type = f_type
        self.left_operand = L_oper
        self.right_operand = R_oper
        self.param = param
        self.entity = entity

        self.sanity_check()

    def __repr__(self):
        if self.f_type == ParamConstraint_oper.param_entity:
            return "{:s}[{:s}]".format(self.param.name, self.entity)
        if self.f_type == ParamConstraint_oper.true:
            return "TRUE"
        if self.f_type == ParamConstraint_oper.l_and:
            return "(" + repr(self.left_operand) + " & " + repr(self.right_operand) + ")"
        if self.f_type == ParamConstraint_oper.l_or:
            return "(" + repr(self.left_operand) + " | " + repr(self.right_operand) + ")"
        if self.f_type == ParamConstraint_oper.l_not:
            return "~(" + repr(self.left_operand) + ")"
        if self.f_type == ParamConstraint_oper.lt:
            return repr(self.left_operand) + " < " + repr(self.right_operand)
        if self.f_type == ParamConstraint_oper.le:
            return repr(self.left_operand) + " <= " + repr(self.right_operand)
        if self.f_type == ParamConstraint_oper.eq:
            return repr(self.left_operand) + " == " + repr(self.right_operand)
        if self.f_type == ParamConstraint_oper.ge:
            return repr(self.left_operand) + " >= " + repr(self.right_operand)
        if self.f_type == ParamConstraint_oper.gt:
            return repr(self.left_operand) + " > " + repr(self.right_operand)

    def sanity_check(self):
        """Sanity checks"""
        for operand in (self.left_operand, self.right_operand):
            if operand:
                if not(
                        isinstance(operand, ParamConstraint)
                        or isinstance(operand, int)):
                    raise RuntimeError(
                        "Unexpected operand type for a bag: {:s} (type: {:s})".format(
                            str(operand), str(type(operand))))

    @classmethod
    def f_param_ent(cls, param, entity_name):
        return cls(ParamConstraint_oper.entity, param=param, entity=entity_name)

    @classmethod
    def f_TRUE(cls):
        return cls(ParamConstraint_oper.true)

    @classmethod
    def f_And(cls, arg_L, arg_R):
        return cls(ParamConstraint_oper.l_and, L_oper=arg_L, R_oper=arg_R)

    @classmethod
    def f_Not(cls, arg):
        return cls(ParamConstraint_oper.l_not, L_oper=arg)

    def __lt__(self, other):
        return ParamConstraint(ParamConstraint_oper.lt, L_oper=self, R_oper=other)

    def __le__(self, other):
        return ParamConstraint(ParamConstraint_oper.le, L_oper=self, R_oper=other)

    def __eq__(self, other):
        return ParamConstraint(ParamConstraint_oper.eq, L_oper=self, R_oper=other)

    def __ge__(self, other):
        return ParamConstraint(ParamConstraint_oper.ge, L_oper=self, R_oper=other)

    def __gt__(self, other):
        return ParamConstraint(ParamConstraint_oper.gt, L_oper=self, R_oper=other)

    def __and__(self, other):
        return ParamConstraint(ParamConstraint_oper.l_and, L_oper=self, R_oper=other)

    def __or__(self, other):
        return ParamConstraint(ParamConstraint_oper.l_or, L_oper=self, R_oper=other)

    def __invert__(self):
        return ParamConstraint(ParamConstraint_oper.l_not, L_oper=self)

# EOF
