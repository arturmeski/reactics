#!/bin/sh

TMPINPUT="tmp_$RANDOM$RANDOM.rs"

CMD="./reactics -zxbB"

for i in `seq 2 9`;do

	echo "[i] n=$i; generating input file"
	in/scripts/gen_tgc_sc.py $i > $TMPINPUT

	for f in `seq 1 2`; do

		echo "[i] Testing formula f$f"

		TMPCMD="$CMD -c f$f $TMPINPUT"
		echo "[i] running reactics: $TMPCMD"

		res=$($TMPCMD | grep STAT)
		mem=$(echo $res | cut -d';' -f 5)
		time=$(echo $res | cut -d';' -f 6)

		echo "[.] Finished. time:$time, mem:$mem"

		echo "$i $time $mem" >> bench_drs_mutex_f$f.dat

	done

	echo 
	
done

rm -f $TMPINPUT

# EOF
