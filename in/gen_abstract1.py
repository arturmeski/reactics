#!/usr/bin/env python

from sys import argv,exit

if len(argv) < 3:
    print "Usage:", argv[0], "<number of modules> <variant>"
    exit(100)

n = int(argv[1])
v = int(argv[2])

if not ( v > 0 and v < 3 ):
    print "unsupported variant"
    exit(100)

print "reactions {"
s = "\t{ {x},{s} -> {a1} };\n"
print s

for i in range(1,n+1):
    s = "\t{ {a" + str(i) + "},{s} -> {y" + str(i) + "} };\n"
    s += "\t{ {a" + str(i) + "},{s} -> {b" + str(i) + "} };\n"
    s += "\t{ {b" + str(i) + "},{s} -> {c" + str(i) + "} };\n"
    s += "\t{ {c" + str(i) + "},{s} -> {d" + str(i) + "} };\n"
    s += "\t{ {d" + str(i) + ",y" + str(i) + "},{s} -> {a" + str(i+1) + "} };\n"
    s += "\t{ {y" + str(i) + "},{s} -> {y" + str(i) + "} };\n"
    print s

s = "\t{ {a" + str(n+1) 
for i in range(1,n+1):
    s += ",y" + str(i)
s += "},{s} -> {r} };\n"
print s
print "}"

if v == 1:
    print "context-entities { s }"
elif v == 2:
    s = "context-entities { s"
    for i in range(1,n+1):
        if i % 2 == 0:
            s += ",a" + str(i)
    s += " }"
    print s

print "initial-contexts { {x} }"
print "rsctl-property { E[{}]F(r) }"
