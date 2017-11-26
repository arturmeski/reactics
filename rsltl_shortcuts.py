from logics import *

##### SHORTCUTS

def bag_True():
    return BagDescription.f_TRUE()

def bag_entity(name):
    return BagDescription.f_entity(name)

def ltl_F(a0, ctx_arg=None):
    if ctx_arg == None:
        ctx_arg = bag_True()
    return Formula_rsLTL.f_F(ctx_arg, a0)

def ltl_G(a0, ctx_arg=None):
    if ctx_arg == None:
        ctx_arg = bag_True()
    return Formula_rsLTL.f_G(ctx_arg, a0)

def ltl_X(a0, ctx_arg=None):
    if ctx_arg == None:
        ctx_arg = bag_True()
    return Formula_rsLTL.f_X(ctx_arg, a0)


