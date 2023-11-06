#!/bin/sh

# sudo systemsetup -getcomputersleep
#sudo systemsetup -setcomputersleep Never
# sudo systemsetup -setcomputersleep 1

REACTICS_SMT="../../reactics-smt"
export PYTHONPATH="$PYTHONPATH:$REACTICS_SMT"

REACTICS_SCRIPT="./pmutex.py"

for i in `seq 2 50`
do
    for special_mode in "p" "np-p" "np-np"
    do
        echo "$i (sm=${special_mode})"
        if [[ $special_mode -eq 1 ]]
        then
            $REACTICS_SCRIPT $i $special_mode
            $REACTICS_SCRIPT -o $i $special_mode
        else
            $REACTICS_SCRIPT $i $special_mode
        fi
    done
done

