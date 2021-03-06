#!/bin/sh
for y in 1 2 3; do
for x in `seq 2 40`;do
    echo $x $y
    filename="results/mutex_f${y}_n${x}_PT.out"
    echo "$x" > $filename
    ./gen_mutex.py $x $y > tmp.rs
    ../main -zcpxvB tmp.rs >&1  >> $filename 
    result="$(tail -1 $filename | sed "s/STAT/$x /")" 
    echo $result >> results/summary_mutex_f${y}_PT.out
    echo $result
    echo
done
done

rm tmp.rs
