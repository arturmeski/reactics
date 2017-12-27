from logics import *

##### SHORTCUTS

def bag_True():
    return BagDescription.f_TRUE()

def bag_entity(name):
    return BagDescription.f_entity(name)

def get_bag_if_str(arg):
    if isinstance(arg, str):
        return bag_entity(arg) > 0
    else:
        return arg

def bag_Not(a0):
    a0 = get_bag_if_str(a0)
    return BagDescription.f_Not(a0)

def bag_And(*args):
    assert len(args) > 1
    last = get_bag_if_str(args[0])
    for arg in args[1:]:
        last = BagDescription.f_And(
            last, get_bag_if_str(arg))
    return last
    
def exact_state(contained_entities, all_entities):
    """
    Assumes 0 concentration level for all the
    not listed entities but present in all_entities
    """
    expr = []
    for ent_str in all_entities:
        ent = bag_entity(ent_str)
        if ent_str in contained_entities:
            expr.append(ent > 0)
        else:
            expr.append(ent == 0)

    if len(expr) > 0:
        
        last = expr[0]
        for e in expr[1:]:
            last = BagDescription.f_And(last, e)
        return last
        
    else:
        assert False

def ltl_F(ctx_arg, a0):
    a0 = get_bag_if_str(a0)
    return Formula_rsLTL.f_F(ctx_arg, a0)

def ltl_G(ctx_arg, a0):
    a0 = get_bag_if_str(a0)
    return Formula_rsLTL.f_G(ctx_arg, a0)

def ltl_X(ctx_arg, a0):
    a0 = get_bag_if_str(a0)
    return Formula_rsLTL.f_X(ctx_arg, a0)

def ltl_And(*args):
    assert len(args) > 1
    last = get_bag_if_str(args[0])
    for arg in args[1:]:
        last = Formula_rsLTL.f_And(last, get_bag_if_str(arg))
    return last

def ltl_Not(a0):
    a0 = get_bag_if_str(a0)
    return Formula_rsLTL.f_Not(a0)
    
def ltl_Implies(a0, a1):
    a0 = get_bag_if_str(a0)
    a1 = get_bag_if_str(a1)
    return Formula_rsLTL.f_Implies(a0, a1)

