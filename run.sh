#!/bin/sh

for i in 2 3 4 5 6 7 8 9 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100;
do
  ./rssmt.py $i | tee "out/result_$i.out" 
  echo "$i: $(tail -1 out/result_$i.out)" >> out/all.out
done