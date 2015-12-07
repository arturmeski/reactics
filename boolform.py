#!/usr/bin/env python

import bftype

class BoolForm:

    def __init__(self, a=None):
        self.initAll()
        if a != None and isinstance(a, int):
            self.setupVarNode(a)

    def initAll(self):
        self.oper = bftype.opertype.unspec

    def setupConjunction(self, lhs, rhs):
        self.oper = bftype.opertype.o_and
        self.sfLeft = lhs
        self.sfRight = rhs

    def setupDisjunction(self, lhs, rhs):
        self.oper = bftype.opertype.o_or
        self.sfLeft = lhs
        self.sfRight = rhs

    def setupNegation(self, form):
        self.oper = bftype.opertype.o_not
        self.subForm = form

    def setupVarNode(self, var_id):
        if not isinstance(var_id, int):
            print("var_id must be an integer")
            raise
        self.oper = bftype.opertype.o_var
        self.varid = var_id

    def __add__(self, x):
        r = BoolForm()
        r.setupDisjunction(self,x)
        return r

    def __mul__(self, x):
        r = BoolForm()
        r.setupConjunction(self,x)
        return r

    def __neg__(self):
        r = BoolForm()
        r.setupNegation(self)
        return r

    def __str__(self):
        if self.oper == bftype.opertype.o_or:
            return "(" + str(self.sfLeft) + " or " + str(self.sfRight) + ")"
        elif self.oper == bftype.opertype.o_and:
            return "(" + str(self.sfLeft) + " and " + str(self.sfRight) + ")"
        elif self.oper == bftype.opertype.o_not:
            return "-" + str(self.subForm)
        elif self.oper == bftype.opertype.o_var:
            return str(self.varid)
        else:
            print("This should not happen. Unknown operator?")
            raise

if __name__ == "__main__":

    y = (BoolForm(1) + -BoolForm(2) * BoolForm(3)) + BoolForm(2)
    
    print(y)

