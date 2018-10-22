#!/bin/sh

TMPINPUT="tmp_$RANDOM$RANDOM.rs"

CMD="./reactics -B"

timelimit="$((30*60))" # 30 minutes

for opt in "z" "zb" "x" "xz" "xzb" "xb" "" "b";do

    for f in `seq 1 3`; do

        done=0

        for i in `seq 2 20`;do

            if [[ $done -eq 1 ]];then
                echo "Skipping f=$f i=$i for $opt"
                continue
            fi

            echo "[i] n=$i; generating input file"
            in/scripts/gen_tgc_sc.py $i > $TMPINPUT

            echo "[i] Testing formula f$f"

            if [[ "$opt" = "" ]];then
                opt_str="NoOpt"
                CMDOPT=""
            else
                opt_str="$opt"
                CMDOPT="-$opt"
            fi

            TMPCMD="$CMD $CMDOPT -c f$f $TMPINPUT"
            echo "[i] running reactics: $TMPCMD"

            res=$(timeout $timelimit $TMPCMD | grep STAT)
	    if [[ $? -ne 0 ]];then
		done=1
            fi
            mem=$(echo $res | cut -d';' -f 5)
            time=$(echo $res | cut -d';' -f 6)

            echo "[.] Finished. time:$time, mem:$mem"

            echo "$i $time $mem" >> bench_drs_tgc_${opt_str}_f$f.dat

        done

        echo 
        
    done

done

rm -f $TMPINPUT

# EOF
