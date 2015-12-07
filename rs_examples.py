#!/usr/bin/env python

from rctsys import ReactionSystem
from rctsys import ReactionSystemWithAutomaton,ContextAutomaton
from distrib_rctsys import DistributedReactionSystem

def toy_ex1():

    rs = ReactionSystem()

    #rs.add_bg_set_entities(["a","b","x","c"])

    #rs.add_reaction(["a","b"],["x"],["c"])
    #rs.add_reaction(["c"],["a"],["a"])
    #rs.add_reaction(["a"],["x"],["c"])
    #rs.set_context_entities(["b"])

    #rs.add_initial_context_set(["a","b"])

    #rs.add_bg_set_entities(["a", "b", "c", "d", "e", "f", "x", "y","1","2","3","4","5","6"])
    rs.add_bg_set_entities(list("qwertyuiopasdfghjklzxcvbnm"))

    rs.add_reaction(["a"], ["x"], ["b"])
    rs.add_reaction(["b"], ["x"], ["c"])
    rs.add_reaction(["c","f"], ["x"], ["d"])
    rs.add_reaction(["d"], ["x"], ["e"])

    rs.set_context_entities(["f","g","h"])
    rs.add_initial_context_set(["a"])

    return rs

def toy_ex2():

    rs = ReactionSystem()

    rs.add_bg_set_entities(["a","b","c","d","d_comp","e","f","x"])
    rs.add_reaction(["a"],["x"],["b"])
    rs.add_reaction(["b"],["a"],["c"])
    rs.add_reaction(["c"],["x"],["d"])
    rs.add_reaction(["d","d_comp"],["e"],["f"])
    rs.add_reaction(["f"],["a"],["e"])
    rs.set_context_entities(["d_comp", "e", "x"])
    rs.add_initial_context_set(["a"])

    return rs

def toy_ex3():

    rs = ReactionSystem()

    rs.add_bg_set_entities(["1","2","3","4"])
    rs.add_reaction(["1","4"],["2"],["1","2"])
    rs.add_reaction(["2"],["3"],["1","3","4"])
    rs.add_reaction(["1","3"],["2"],["1","2"])
    rs.add_reaction(["3"],["2"],["1"])
    rs.add_initial_context_set(["1","4"])
    rs.set_context_entities(["4"])

    return rs

def bitctr(bits):

    rs = ReactionSystem()

    n = bits

    for i in range(0,bits):
        rs.addBgSetEntity("p" + str(i))

    rs.addBgSetEntity("dec")
    rs.addBgSetEntity("inc")

    # (1) no dec, no inc
    for j in range(0,bits):
        rs.add_reaction(["p"+str(j)], ["dec","inc"], ["p"+str(j)])

    # (2) increment
    rs.add_reaction(["inc"],["dec","p0"],["p0"])
    for j in range(1,bits):
        R = ["inc"]
        for k in range(0,j):
            R.append("p"+str(k))
        I = ["dec","p"+str(j)]
        P = ["p"+str(j)]
        rs.add_reaction(R, I, P)

    for j in range(0,bits):
        for k in range(j+1,bits):
            rs.add_reaction(["inc","p"+str(k)], ["dec","p"+str(j)], ["p"+str(k)])

    # (3) decrement
    for j in range(0,bits):
        R=["dec"]
        I=["inc"]
        for k in range(0,j+1):
            I.append("p"+str(k))
        P=["p"+str(j)]
        rs.add_reaction(R, I, P)

    for j in range(0,bits):
        for k in range(j+1,bits):
            rs.add_reaction(["dec","p"+str(j),"p"+str(k)], ["inc"], ["p"+str(k)])

    rs.set_context_entities(["dec","inc"])
    rs.add_initial_context_set(["inc"])
    
    return rs
    

def ca_toy_ex1():

    rs = ReactionSystem()

    rs.add_bg_set_entities(list("axbcdfegh"))

    rs.add_reaction(["a"], ["x"], ["b"])
    rs.add_reaction(["b"], ["x"], ["c"])
    rs.add_reaction(["c","f"], ["x"], ["d"])
    rs.add_reaction(["d"], ["x"], ["e"])

    #rs.set_context_entities(["f","g","h"])
    #rs.add_initial_context_set(["a"])

    ca = ContextAutomaton(rs)
    ca.add_init_state("1")
    ca.add_state("2")
    ca.add_transition("1", ["a"], "2")
    ca.add_transition("2", [], "2")
    ca.add_transition("2", ["f"], "2")
    ca.add_transition("2", ["x"], "2")

    rsca = ReactionSystemWithAutomaton(rs,ca)

    return rsca

def ca_toy_ex1_property1():
    return ["e"]


def drs_toy_ex1():
    
    drs = DistributedReactionSystem()
    drs.add_bg_set_entities(list("axbcd"))
    drs.add_reaction(0, ["a"], ["x"], ["b"])
    drs.add_reaction(0, ["b"], ["c"], ["d"])
    drs.add_reaction(1, ["a"], [], ["b"])
    
    drs.add_init_state("init")
    drs.add_state("working")
    drs.add_transition("init", ([0],[ ["a"], ["a"] ]), "working")
    drs.add_transition("working", ([1],[ ["b"], ["a"] ]), "working")
    
    return drs

def drs_toy_ex1_property1():
    return [["b"],["b"]]
    
def drs_mutex(k):
    
    drs = DistributedReactionSystem()

    ctrl = k
    # agents = 0 ... (k-1) 

    drs.add_bg_set_entities(["lock", "busy", "release", "req", "out", "in"])
    
    drs.add_reaction(ctrl, ["lock"], ["release"], ["lock"])
    drs.add_reaction(ctrl, ["req"], [], ["lock"])

    for i in range(k):
        #drs.add_reaction(i, ["out"], [], ["req"])
        drs.add_reaction(i, ["out","busy"], [], ["out"])
        drs.add_reaction(i, ["out"], [], ["req"])
        drs.add_reaction(i, ["req"], ["lock"], ["in"])
        drs.add_reaction(i, ["in"], ["busy"], ["out","release"])
        drs.add_reaction(i, ["in","busy"], [], ["in"])
        drs.add_reaction(i, ["req", "lock"], [], ["req"])

    drs.add_init_state("0")
    drs.add_state("1")
    
    all_out = [["out"] for i in range(k)]
    all_out.append([]) # empty context for the controller

    all_empty = [[] for i in range(k+1)]
    
    drs.add_transition("0", ([i for i in range(k+1)], all_out), "1")
    for i in range(k):
        drs.add_transition("1", ([i,ctrl], all_empty), "1")
        one_busy = [[] for x in range(k+1)]
        one_busy[i] = ["busy"]
        drs.add_transition("1", ([i,ctrl], one_busy), "1")
    
    return drs
    
def drs_mutex_property1(k):
    state = [["in"]]
    state.extend([[] for i in range(k)])
    
    return state
    