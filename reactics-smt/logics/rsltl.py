from z3 import *
from enum import Enum

from logics.bags import *

rsLTL_form_type = Enum(
    'rsLTL_form_type',
    'bag l_and l_or l_not l_implies t_globally t_finally t_next t_until t_release')


class Formula_rsLTL(object):

    def __init__(
            self, f_type, L_oper=None, R_oper=None, sub_oper=None, bag=None):
        self.f_type = f_type
        self.left_operand = L_oper
        self.right_operand = R_oper
        self.sub_operand = sub_oper
        self.bag_descr = bag

        # it's silly, but it's a frequent mistake
        if callable(sub_oper):
            raise RuntimeError(
                "sub_oper should not be a function. Missing () for {0}?".format(sub_oper))

        if isinstance(self.left_operand, BagDescription):
            self.left_operand = Formula_rsLTL.f_bag(self.left_operand)
        if isinstance(self.right_operand, BagDescription):
            self.right_operand = Formula_rsLTL.f_bag(self.right_operand)

        if self.sub_operand is True:
            self.sub_operand = BagDescription.f_TRUE()

    def __repr__(self):
        if self.f_type == rsLTL_form_type.bag:
            return repr(self.bag_descr)
        if self.f_type == rsLTL_form_type.l_not:
            return "~(" + repr(self.left_operand) + ")"
        if self.f_type == rsLTL_form_type.t_globally:
            return "G[" + repr(self.sub_operand) + "](" + repr(self.left_operand) + ")"
        if self.f_type == rsLTL_form_type.t_finally:
            return "F[" + repr(self.sub_operand) + "](" + repr(self.left_operand) + ")"
        if self.f_type == rsLTL_form_type.t_next:
            return "X[" + repr(self.sub_operand) + "](" + repr(self.left_operand) + ")"
        if self.f_type == rsLTL_form_type.l_and:
            return "(" + repr(self.left_operand) + " & " + repr(self.right_operand) + ")"
        if self.f_type == rsLTL_form_type.l_or:
            return "(" + repr(self.left_operand) + " | " + repr(self.right_operand) + ")"
        if self.f_type == rsLTL_form_type.l_implies:
            return "(" + repr(self.left_operand) + " => " + repr(self.right_operand) + ")"
        if self.f_type == rsLTL_form_type.t_until:
            return "(" + repr(
                self.left_operand) + " U[" + repr(
                self.sub_operand) + "] " + repr(
                self.right_operand) + ")"
        if self.f_type == rsLTL_form_type.t_release:
            return "(" + repr(
                self.left_operand) + " R[" + repr(
                self.sub_operand) + "] " + repr(
                self.right_operand) + ")"

    @property
    def is_bag(self):
        return self.f_type == rsLTL_form_type.bag

    @classmethod
    def f_bag(cls, bag_descr):
        return cls(rsLTL_form_type.bag, bag=bag_descr)

    @classmethod
    def f_Not(cls, arg):
        return cls(rsLTL_form_type.l_not, L_oper=arg)

    @classmethod
    def f_And(cls, arg_L, arg_R):
        return cls(rsLTL_form_type.l_and, L_oper=arg_L, R_oper=arg_R)

    @classmethod
    def f_Or(cls, arg_L, arg_R):
        return cls(rsLTL_form_type.l_or, L_oper=arg_L, R_oper=arg_R)

    @classmethod
    def f_Implies(cls, arg_L, arg_R):
        return cls(rsLTL_form_type.l_implies, L_oper=arg_L, R_oper=arg_R)

    @classmethod
    def f_X(cls, sub, arg):
        return cls(rsLTL_form_type.t_next, L_oper=arg, sub_oper=sub)

    @classmethod
    def f_G(cls, sub, arg):
        return cls(rsLTL_form_type.t_globally, L_oper=arg, sub_oper=sub)

    @classmethod
    def f_U(cls, sub, arg_L, arg_R):
        return cls(
            rsLTL_form_type.t_until, L_oper=arg_L, R_oper=arg_R, sub_oper=sub)

    @classmethod
    def f_F(cls, sub, arg_L):
        return cls(rsLTL_form_type.t_finally, L_oper=arg_L, sub_oper=sub)

    @classmethod
    def f_R(cls, sub, arg_L, arg_R):
        return cls(
            rsLTL_form_type.t_release, L_oper=arg_L, R_oper=arg_R,
            sub_oper=sub)

    def __and__(self, other):
        return Formula_rsLTL(rsLTL_form_type.l_and, L_oper=self, R_oper=other)

    def __or__(self, other):
        return Formula_rsLTL(rsLTL_form_type.l_or, L_oper=self, R_oper=other)

    def __invert__(self):
        return Formula_rsLTL(rsLTL_form_type.l_not, L_oper=self)


# EOF
