#!/bin/sh
for y in `seq 0 2`; do
for x in `seq 2 1 24`;do
    echo $y $x
    filename="results/f${y}_n${x}.out"
    echo "$x" > $filename
    ./gen_bc.py $x $y > tmp.rs
    ../main -c -B tmp.rs  >> $filename
    result="$(tail -1 $filename | sed "s/STAT/$x /")" 
    echo $result >> results/summary_f${y}.out
    echo $result
    echo
done
done

rm tmp.rs
