#!/usr/bin/env python

from sys import argv,exit

if len(argv) < 2:
    print "Usage:", argv[0], "<number of bits>"
    exit(100)

n = int(argv[1])

print "reactions {"

# (1) no dec, no inc
print "\t# (1) no decrement, no increment"
for j in range(0,n):
    print "\t{ { p" + str(j) + "; },{ dec; inc; } -> { p" + str(j) + "; } };"

# (2) increment
print "\n\t# (2) increment operation"
for j in range(0,n):
    print "\t{ { inc;",
    for k in range(0,j):
        print "p" + str(k) + ";",
    print "},{ dec; p" + str(j) + "; } -> { p" + str(j) + "; } };"
   
    print "\t# the more significant bits remain (inc)"
    for k in range(j,n):
        print "\t{ { inc; p" + str(k) + "; },{ dec; p" + str(j) + "; } -> { p" + str(k) + "; } };"
    print

print "\n\t# (3) decrement operation"
for j in range(0,n):
    print "\t{ { dec; },{ inc;",
    for k in range(0,j):
        print "p" + str(k) + ";",
    print "} -> { p" + str(j) + "; } };"

    print "\t# the more significant bits remain (dec)"
    for k in range(j,n):
        print "\t{ { dec; p" + str(j) + "; p" + str(k) + "; },{ inc; } -> { p" + str(k) + "; } };"
    print

print "}"

print "action-atoms { inc; dec; }"
print "initial-state { }"

print "ctl-property { AG( p" + str(n-1) + " IMPLIES EF ~p" + str(n-1) + " ) }"
