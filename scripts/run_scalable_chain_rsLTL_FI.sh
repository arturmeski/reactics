#!/bin/sh

# sudo systemsetup -getcomputersleep
sudo systemsetup -setcomputersleep Never
# sudo systemsetup -setcomputersleep 1

formula=1
for i in `seq 2 50`
do
	echo $i
	./rssmt.py $i 2 $formula
done

formula=2
for i in `seq 2 50`
do
	echo $i
	./rssmt.py $i 2 $formula
done

formula=3
for i in `seq 2 50`
do
	echo $i
	./rssmt.py $i 2 $formula
done

formula=4
for i in `seq 2 50`
do
	echo $i
	./rssmt.py $i 2 $formula
done

