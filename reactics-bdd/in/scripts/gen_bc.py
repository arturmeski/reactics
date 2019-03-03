#!/usr/bin/env python2.7

from sys import argv,exit


if len(argv) < 3:
    print "Usage:", argv[0], "<number of bits> <property>"
    exit(100)

n = int(argv[1])
property = int(argv[2])

K = 8
if property == 3:
    if n < K+1:
        print "too small n"
        exit(100)

if not ( property >= 1 and property < 5 ):
    print "property: 1-4"
    exit(101)

print "reactions {"

# (1) no dec, no inc
print "\t# (1) no decrement, no increment"
for j in range(0,n):
    print "\t{{p" + str(j) + "},{dec,inc} -> {p" + str(j) + "}};"

# (2) increment
s = "\n\t# (2) increment operation\n"
s += "\t{{inc},{dec,p0} -> {p0}};\n"
for j in range(1,n):
    s += "\t{{inc,"
    for k in range(0,j):
        s += "p" + str(k)
        if k < j-1:
            s += ","
    s += "},{dec,p" + str(j) + "} -> {p" + str(j) + "}};\n"

print s

print "\t# the more significant bits remain (inc)"
s = ""
for j in range(0,n):
    for k in range(j+1,n):
        s += "\t{{inc,p" + str(k) + "},{dec,p" + str(j) + "} -> {p" + str(k) + "}};\n"

print s

print "\t# (3) decrement operation"
s = ""
for j in range(0,n):
    s += "\t{{dec},{inc,"
    for k in range(0,j+1):
        s += "p" + str(k)
        if k < j:
            s += ","
    s += "} -> {p" + str(j) + "}};\n"
print s

print "\t# the more significant bits remain (dec)"
s = ""
for j in range(0,n):
    for k in range(j+1,n):
        s += "\t{{dec,p" + str(j) + ",p" + str(k) + "},{inc} -> {p" + str(k) + "}};\n"

s += "}\n"
print s

print "context-entities { inc,dec }"
print "initial-contexts { {} }"

if property == 4:
    print "rsctl-property { AG( p" + str(n-1) + " IMPLIES EF ~p" + str(n-1) + " ) }"
elif property == 1:
    s = "rsctl-property { AG(("
    for i in range(0,n):
        s += "~p" + str(i)
        if i < n-1:
            s += " AND "
    s += ") IMPLIES E[{inc},{dec}]F("
    for i in range(0,n):
        s += "p" + str(i)
        if i < n-1:
            s += " AND "
 
    s += ")) }"
    print s
elif property == 2:
    s = "rsctl-property { AG(("
    for i in range(0,n):
        s += "p" + str(i)
        if i < n-1:
            s += " AND "
    s += ") IMPLIES A[{inc}]X("
    for i in range(0,n):
        s += "~p" + str(i)
        if i < n-1:
            s += " AND "
 
    s += ")) }"
    print s

elif property == 3:
    s = "rsctl-property { E[{inc}]F("
    for i in range(0,n-K):
        s += "p" + str(i)
        if i < n-1:
            s += " AND "
    for i in range(n-K,n):
        s += "~p" + str(i)
        if i < n-1:
            s += " AND "
    s += ") }"
    print s


