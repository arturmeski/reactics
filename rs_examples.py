#!/usr/bin/env python

from rs import *
from smt import *
import sys
import resource

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
    # r.add_bg_set_entity(("reset",1))
    r.add_bg_set_entity(("dec",1))
    # r.add_bg_set_entity(("x",1))
    
    for i in range(1,chainLen+1):
        r.add_bg_set_entity(("e_" + str(i),maxConc))
    
    for i in range(1,chainLen+1):
        ent = "e_" + str(i)
        # r.add_reaction_inc(ent, "inc", [(ent, 1)],[("reset",1),(ent,maxConc)])
        r.add_reaction_inc(ent, "inc", [(ent, 1)],[(ent,maxConc)])
        r.add_reaction_dec(ent, "dec", [(ent, 1)],[])
        # r.add_reaction([(ent,1),("reset",1)],[],[(ent,1)])
        if i < chainLen:
            r.add_reaction([(ent,maxConc)],[],[("e_"+str(i+1),1)])

    r.add_reaction([("e_" + str(chainLen),maxConc)],[("dec",1)],[("e_" + str(chainLen),maxConc)])
    # r.add_reaction([("e_" + str(chainLen),maxConc)],[],[("e_" + str(chainLen),maxConc)])
    
    
    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1",1),("inc",1)], "working")
    c.add_transition("working", [("inc",1)], "working")
    # c.add_transition("working", [("reset",1)], "working")
    # c.add_transition("working",[("x",1)],"working")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    if verify_rsc:
        smt_rsc = SmtCheckerRSC(rc)
        prop = [('e_'+str(chainLen),maxConc)]
        smt_rsc.check_reachability((prop,[]),max_level=maxConc*chainLen+10)
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


def heat_shock_response(print_system=True,verify_rsc=True):

    if len(sys.argv) < 1+1:
        print("provide B")
        print(" B=1 - RSC")
        print(" B=0 - Translated RSC into RS")
        exit(1)

    verify_rsc=bool(int(sys.argv[1]))

    stress_temp = 42
    max_temp = 50
    
    r = ReactionSystemWithConcentrations()    
    r.add_bg_set_entity(("hsp",1))
    r.add_bg_set_entity(("hsf",1))
    r.add_bg_set_entity(("hsf2",1))
    r.add_bg_set_entity(("hsf3",1))
    r.add_bg_set_entity(("hse",1))
    r.add_bg_set_entity(("mfp",1))
    r.add_bg_set_entity(("prot",1))
    r.add_bg_set_entity(("hsf3:hse",1))
    r.add_bg_set_entity(("hsp:mfp",1))
    r.add_bg_set_entity(("hsp:hsf",1))
    r.add_bg_set_entity(("temp",max_temp))
    r.add_bg_set_entity(("heat",1))
    r.add_bg_set_entity(("cool",1))
    
    r.add_reaction([("hsf",1)],                         [("hsp",1)],        [("hsf3",1)])
    r.add_reaction([("hsf",1),("hsp",1),("mfp",1)],     [],                 [("hsf3",1)])
    r.add_reaction([("hsf3",1)],                        [("hse",1),("hsp",1)],[("hsf",1)])
    r.add_reaction([("hsf3",1),("hsp",1),("mfp",1)],    [("hse",1)],        [("hsf",1)])
    r.add_reaction([("hsf3",1),("hse",1)],              [("hsp",1)],        [("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("mfp",1),("hse",1)],[],           [("hsf3:hse",1)])
    r.add_reaction([("hse",1)],                         [("hsf3",1)],       [("hse",1)])
    r.add_reaction([("hsp",1),("hsf3",1),("hse",1)],    [("mfp",1)],        [("hse",1)])
    r.add_reaction([("hsf3:hse",1)],                    [("hsp",1)],        [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsp",1),("mfp",1),("hsf3:hse",1)],[],                 [("hsp",1),("hsf3:hse",1)])
    r.add_reaction([("hsf",1),("hsp",1)],               [("mfp",1)],        [("hsp:hsf",1)])
    r.add_reaction([("hsp:hsf",1),("temp",stress_temp)],[],                 [("hsf",1),("hsp",1)])
    r.add_reaction([("hsp:hsf",1)],                     [("temp",stress_temp)],[("hsp:hsf",1)])
    r.add_reaction([("hsp",1),("hsf3:hse",1)],          [("mfp",1)],        [("hse",1),("hsp:hsf",1)])
    r.add_reaction([("temp",stress_temp),("prot",1)],   [],                     [("mfp",1),("prot",1)])
    r.add_reaction([("prot",1)],                        [("temp",stress_temp)], [("prot",1)])
    r.add_reaction([("hsp",1),("mfp",1)],               [],                 [("hsp:mfp",1)])
    r.add_reaction([("mfp",1)],                         [("hsp",1)],        [("mfp",1)])
    r.add_reaction([("hsp:mfp",1)],                     [],                 [("hsp",1),("prot",1)])

    r.add_reaction_inc("temp", "heat", [("temp",1)],[("temp",max_temp)])
    r.add_reaction_dec("temp", "cool", [("temp",1)],[])

    r.add_permanency("temp",[("heat",1),("cool",1)])
    #r.add_permanency("temp",[])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    # c.add_transition("0", [("prot",1), ("temp",35)], "1")
    c.add_transition("0", [("hsf",1),("prot",1),("hse",1),("temp",35)], "1")
    #-> c.add_transition("0", [("hse",1),("prot",1),("hsp:hsf",1),("temp",stress_temp)], "1")
    # c.add_transition("0", [("hsp",1),("prot",1),("hsf3:hse",1),("mfp",1),("hsp:mfp",1),("temp",30)], "1")
    c.add_transition("1", [("cool",1)], "1")
    c.add_transition("1", [("heat",1)], "1")
    c.add_transition("1", [], "1")
    # c.add_transition("1", [("sugar",1)], "1")

    rc = ReactionSystemWithAutomaton(r,c)
    
    if print_system:
        rc.show()
    
    # prop_req = [("hsp:hsf",1),("hse",1),("prot",1)]
    # prop_block = [("temp",stress_temp)]
    prop_req   = [ ("mfp",1) ]
    prop_block = [ ]
    prop       = (prop_req,prop_block)
    rs_prop    = (state_translate_rsc2rs(prop_req),state_translate_rsc2rs(prop_block))
    
    if verify_rsc:
        smt_rsc = SmtCheckerRSC(rc)
        smt_rsc.check_reachability(prop,max_level=40)
    else:
        orc = rc.get_ordinary_reaction_system_with_automaton()
        if print_system:
            print("\nTranslated:")
            orc.show()
        smt_tr_rs = SmtCheckerPGRS(orc)
        smt_tr_rs.check_reachability(rs_prop)

def state_translate_rsc2rs(p):
    return [e[0] + "#" + str(e[1]) for e in p]
        
