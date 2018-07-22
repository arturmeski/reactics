#!/bin/sh

TMPINPUT="tmp_$RANDOM$RANDOM.rs"

CMD="./reactics -b -B"

for i in `seq 2 10`;do

	echo "[i] n=$i; generating input file"
	in/gen_drs_mutex.py $i > $TMPINPUT

	for f in `seq 1 2`; do

		echo "[i] Testing formula f$f"

		TMPCMD="$CMD -c f$f $TMPINPUT"
		echo "[i] running reactics: $TMPCMD"

		res=$($TMPCMD | grep STAT)
		mem=$(echo $res | cut -d';' -f 5)
		time=$(echo $res | cut -d';' -f 6)

		echo "[.] Finished. time:$time, mem:$mem"

		echo "$i $time $mem"  >> results_f$f.out

	done

	echo 
	
done

rm -f $TMPINPUT

# EOF