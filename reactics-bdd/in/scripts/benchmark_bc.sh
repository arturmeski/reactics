#!/bin/sh
for y in 2; do
for x in `seq 1 50`;do
    echo $x $y
    filename="results/bc_f${y}_n${x}.out"
    echo "$x" > $filename
    ./gen_bc.py $x $y > tmp.rs
    ../main -z -c -v -B tmp.rs >&1  >> $filename 
    result="$(tail -1 $filename | sed "s/STAT/$x /")" 
    echo $result >> results/summary_bc_f${y}.out
    echo $result
    echo
done
done

rm tmp.rs
