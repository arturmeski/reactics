#!/usr/bin/env python

from rctsys import ReactionSystem,ReactionSystemWithConcentrations,ContextAutomatonWithConcentrations,ReactionSystemWithAutomaton
from distrib_rctsys import DistributedReactionSystem
from smtchecker import SmtChecker
from smtcheckerpgrs import SmtCheckerPGRS
from smtcheckerdistribrs import SmtCheckerDistribRS
from smtcheckerrsc import SmtCheckerRSC
import sys
import resource

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


def ca_bitctr(bits):

    rs = ReactionSystem()

    n = bits

    for i in range(0,bits):
        rs.add_bg_set_entities(["p" + str(i)])

    rs.add_bg_set_entities(["dec"])
    rs.add_bg_set_entities(["inc"])

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

    ca = ContextAutomaton(rs)
    ca.add_init_state("1")
    ca.add_transition("1", ["inc"], "1")
    ca.add_transition("1", ["inc","dec"], "1")
    ca.add_transition("1", ["dec"], "1")
    
    rsca = ReactionSystemWithAutomaton(rs,ca)
    
    return rsca
    
def ca_bitctr_property(bits):
    
    state = []
    
    for i in range(0,bits):
        state.append("p"+str(i))
        
    return state

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

def run_counter_exp():

    if len(sys.argv) < 1+1:
        print("provide N")
        exit(1)
    
    N=int(sys.argv[1])

    r = ReactionSystemWithConcentrations()

    r.add_bg_set_entity("e")
    r.add_bg_set_entity("inc")    
    r.add_reaction_inc("e",[("e",1),("inc",1)],[("e",N)])
    # for i in range(1,N):
        # r.add_reaction([("e",i),("inc",1)],[("e",N)],[("e",i+1)])
    # r.show()
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")
     # c.show()

    rc = ReactionSystemWithAutomaton(r,c)
    
    rc.show()
    
    smt_rsc = SmtCheckerRSC(rc)    
    smt_rsc.check_reachability([('e',N)],print_time=True,max_level=N)

    orc = rc.get_ordinary_reaction_system_with_automaton()
    orc.show()
    smt_tr_rs = SmtCheckerPGRS(orc)
    smt_tr_rs.check_reachability(['e_' + str(N)],print_time=True)

    print("Reaction System with Concentrations:", smt_rsc.get_verification_time())
    print("Reaction System from translating RSC:", smt_tr_rs.get_verification_time())

def chain_reaction(print_system=False):
    
    if len(sys.argv) < 1+3:
        print("provide N M B")
        print(" B=1 - RSC")
        print(" B=0 - Translated RSC into RS")
        exit(1)

    chainLen=int(sys.argv[1]) # chain length
    maxConc=int(sys.argv[2]) # depth (max concentration)
    verify_rsc=bool(int(sys.argv[3]))
        
    if chainLen < 1 or maxConc < 1:
        print("be reasonable")
        exit(1)
    
    r = ReactionSystemWithConcentrations()    
    r.add_bg_set_entity(("inc",1))
    r.add_bg_set_entity(("dec",1))
    
    for i in range(1,chainLen+1):
        r.add_bg_set_entity("e_" + str(i))
    
    for i in range(1,chainLen+1):
        ent = "e_" + str(i)
        r.add_reaction_inc(ent, "inc", [(ent, 1)],[(ent,maxConc)])
        r.add_reaction_dec(ent, "dec", [(ent, 1)],[])
        if i < chainLen:
            r.add_reaction([(ent,maxConc)],[],[("e_"+str(i+1),1)])

    r.add_reaction([("e_" + str(chainLen),maxConc)],[("dec",1)],[("e_" + str(chainLen),maxConc)])
        
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    if verify_rsc:
        smt_rsc = SmtCheckerRSC(rc)
        prop = [('e_'+str(chainLen),maxConc)]
        smt_rsc.check_reachability(prop,max_level=maxConc*chainLen+10)
        # smt_rsc.show_encoding(prop,print_time=True,max_level=maxConc*chainLen+10)

    else:
        orc = rc.get_ordinary_reaction_system_with_automaton()
        if print_system:
            print("\nTranslated:")
            orc.show()
        smt_tr_rs = SmtCheckerPGRS(orc)
        smt_tr_rs.check_reachability(['e_'+str(chainLen)+"#"+str(maxConc)])
    
    # print("Reaction System with Concentrations:", smt_rsc.get_verification_time())
    # print("Reaction System from translating RSC:", smt_tr_rs.get_verification_time())
    
    filename=""
    time=0
    mem_usage=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024*1024)
    if verify_rsc:
        filename_t="bench_rsc_time.log"
        filename_m="bench_rsc_mem.log"
        time=smt_rsc.get_verification_time()
    else:
        filename_t="bench_tr_rs_time.log"
        filename_m="bench_tr_rs_mem.log"
        time=smt_tr_rs.get_verification_time()

    f=open(filename_t, 'a')    
    log_str="(" + str(chainLen) + "," + str(maxConc) + "," + str(time) + ")\n"
    f.write(log_str)
    f.close()
    
    f=open(filename_m, 'a')
    log_str="(" + str(chainLen) + "," + str(maxConc) + "," + str(mem_usage) + ")\n"
    f.write(log_str)
    f.close()

def blood_glucose_regulation():
    
    r = ReactionSystemWithConcentrations()    
    r.add_bg_set_entity(("inc_insulin",1))
    r.add_bg_set_entity(("dec_insulin",1))
    r.add_bg_set_entity(("inc_glycemia",1))
    r.add_bg_set_entities(("inc_"))
    
    r.add_bg_set_entities([(sugar,1),(aspartame,1),(glycemia,3),(glucagon,1),(insulin,2)])
    
    # r.add_reaction([],[],[])
    r.add_reaction([(sugar,1)],[],[(inc_insulin,1),(inc_glycemia,1)])
    r.add_reaction([],[],[])
    r.add_reaction([],[],[])
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    # if verify_rsc:
    #     smt_rsc = SmtCheckerRSC(rc)
    #     prop = [('e_'+str(chainLen),maxConc)]
    #     smt_rsc.check_reachability(prop,max_level=maxConc*chainLen+10)
    #     # smt_rsc.show_encoding(prop,print_time=True,max_level=maxConc*chainLen+10)
