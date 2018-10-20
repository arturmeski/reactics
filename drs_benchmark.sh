#!/bin/sh

TMPINPUT="tmp_$RANDOM$RANDOM.rs"

CMD="./reactics -bB"

for opt in "" "z" "x" "zx";do

    for i in `seq 2 10`;do

        echo "[i] n=$i; generating input file"
        in/scripts/gen_tgc_sc.py $i > $TMPINPUT

        for f in `seq 1 2`; do

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

            res=$($TMPCMD | grep STAT)
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
