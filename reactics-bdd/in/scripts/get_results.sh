#!/bin/sh

test -z "$1" && exit 1
cd $1
for f in `ls *.out | sort -n`; do
    n="$(head -1 $f)"
    res="$(tail -1 $f)"
    enct="$(echo $res | cut -f 2 -d';')"
    vert="$(echo $res | cut -f 3 -d';')"
    encm="$(echo $res | cut -f 4 -d';')"
    verm="$(echo $res | cut -f 5 -d';')"
    tott="$(echo $res | cut -f 6 -d';')"
    echo "$n $enct $vert $encm $verm $tott"
done
