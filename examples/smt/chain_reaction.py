#!/usr/bin/env python
#
# Copyright (c) 2015-2019 Artur Meski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from rs import *
from smt import *
import sys
import resource

def chain_reaction(print_system=False):
    
    if len(sys.argv) < 1+3:
        print("provide N M B")
        print(" B=1 - RSC")
        print(" B=0 - RSC translated into RS")
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
        r.add_bg_set_entity(("e_" + str(i),maxConc))
    
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
        smt_rsc.check_reachability((prop,[]),max_level=maxConc*chainLen+10)

    else:
        orc = rc.get_ordinary_reaction_system_with_automaton()
        if print_system:
            print("\nTranslated:")
            orc.show()
        smt_tr_rs = SmtCheckerRS(orc)
        smt_tr_rs.check_reachability(['e_'+str(chainLen)+"#"+str(maxConc)])
    
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


def main():

    chain_reaction()

if __name__ == "__main__":
    main()
        
# EOF
