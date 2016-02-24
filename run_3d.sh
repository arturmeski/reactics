#!/bin/sh

# sudo systemsetup -getcomputersleep 
# sudo systemsetup -setcomputersleep Never
# sudo systemsetup -setcomputersleep 1



for i in `seq 1 20`
do
  #./rssmt.py $i | tee "out/result_$i.out" 
  #echo "$i: $(tail -1 out/result_$i.out)" >> out/all.out
  echo $i
  for j in `seq 1 20`
  do
    echo $i $j
	for t in 1 0
	do
	    ./rssmt.py $i $j $t
	done
  done
done


