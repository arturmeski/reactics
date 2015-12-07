#!/usr/bin/env python

from rctsys import *
import rs_examples

rs = rs_examples.toy_ex3()

ca = ContextAutomaton(rs)

ca.add_state("st1")
ca.add_init_state("in")

ca.add_transition("st1", {"1","2"}, "in")

ca.show()

