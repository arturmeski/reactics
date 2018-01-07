#!/bin/sh

# sudo systemsetup -getcomputersleep
#sudo systemsetup -setcomputersleep Never
# sudo systemsetup -setcomputersleep 1

for i in `seq 2 20`
do
	echo $i
	./rssmt.py -o -n $i 
done

