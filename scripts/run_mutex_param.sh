#!/bin/sh

# sudo systemsetup -getcomputersleep
#sudo systemsetup -setcomputersleep Never
# sudo systemsetup -setcomputersleep 1

for i in `seq 2 100`
do
    for special_mode in 1 2
    do
        echo "$i (sm=${special_mode})"
        if [[ $special_mode -eq 1 ]]
        then
            ./rssmt.py -n $i -s $special_mode
            ./rssmt.py -o -n $i -s $special_mode
        else
            ./rssmt.py -n $i -s $special_mode
        fi
    done
done

