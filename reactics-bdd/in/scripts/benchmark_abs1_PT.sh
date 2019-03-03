#!/bin/sh
for y in 1 2; do
for x in `seq 1 60`;do
    echo $x
    filename="results/abs_v${y}_f0_n${x}_PT.out"
    echo "$x" > $filename
    ./gen_abstract1.py $x $y > tmp.rs
    ../main -z -x -c -p -v -B tmp.rs >&1  >> $filename 
    result="$(tail -1 $filename | sed "s/STAT/$x /")" 
    echo $result >> results/summary_v${y}_abs_f0_PT.out
    echo $result
    echo
done
done

rm tmp.rs
