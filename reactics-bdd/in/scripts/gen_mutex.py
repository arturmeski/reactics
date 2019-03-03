#!/usr/bin/env python

from sys import argv,exit


if len(argv) < 3:
    print "Usage:", argv[0], "<number of processes> <formula>"
    exit(100)

n = int(argv[1])
f = int(argv[2])

if not ( f>0 and f<4 ):
    print "unsupported formula"
    exit(100)

print "reactions {"
for i in range(0,n):
    s = "\t{{out" + str(i) + ",act" + str(i) + "},{} -> {request" + str(i) + "}};\n"
    s += "\t{{out" + str(i) + "},{act" + str(i) + "} -> {out" + str(i) + "}};\n"
    for j in range(0,n):
        if i != j:
            s += "\t{{request" + str(i) + ",act" + str(i) + ",act" + str(j) + "},{} -> {request" + str(i) + "}};\n"
    #s += "\t{{request" + str(i) + "},{"
    #for j in range(0,n):
    #    s += "act" + str(j)
    #    if j < n-1:
    #        s += ","
    #s += "} -> {request" + str(i) + "}};\n"
    s += "\t{{request" + str(i) + "},{act" + str(i) + "} -> {request" + str(i) + "}};\n"
    s += "\t{{request" + str(i) + ",act" + str(i) + "},{"
    for j in range(0,n):
        if i != j:
            s += "act" + str(j) + ","
    s += "lock} -> {in" + str(i) + ",lock}};\n"
    s += "\t{{in" + str(i) + ",act" + str(i) + "},{} -> {out" + str(i) + ",done}};\n"
    s += "\t{{in" + str(i) + "},{act" + str(i) + "} -> {in" + str(i) + "}};\n"
    print s

print "\t{{lock},{done} -> {lock}};"

print "}"

s = "context-entities {"
for i in range(0,n):
    s += "act" + str(i)
    if i < n-1:
        s += ","
s += "}\n"
print s

s = "initial-contexts { {"
for i in range(0,n):
    s += "out" + str(i)
    if i < n-1:
        s += ","
s += "} }\n"
print s

#print "rsctl-property { A[{act1}]G(A[{act1}]F(in1)) }"
if f == 1:
    print "rsctl-property { A[{act1}]F(in1) }"
elif f == 2:
    print "rsctl-property { E[{act1}]F(in1) }"
elif f == 3:
    s = "rsctl-property { AG("
    for i in range(0,n):
        for j in range(i+1,n):
            s += "~(in" + str(i) + " AND in" + str(j) + ")"
            if i < n-2:
                s += " AND "
    s += ") }"
    print s
else:
    exit(111)

