#!/bin/sh

TMPINPUT="tmp_$RANDOM$RANDOM.rs"

CMD="./reactics -B"

timelimit="$((30*60))" # 30 minutes
timelimit="$((5*60))" # 5 minutes

form_tgc_sc="`seq 1 3`"
form_asm="`seq 1 2`"

for benchmark in "tgc_sc" "asm"; do

    eval formulae=\$form_${benchmark}

    for opt in "z" "zb" "x" "xz" "xzb" "xb" "" "b";do

        for f in $formulae; do

            done=0

            for i in `seq 2 20`;do

                if [[ $done -eq 1 ]];then
                    echo "Skipping f=$f i=$i for $opt"
                    continue
                fi

                echo "[i] n=$i; generating input file (${benchmark})"
                in/scripts/gen_${benchmark}.py $i > $TMPINPUT

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
                    continue
                fi
                mem=$(echo $res | cut -d';' -f 5)
                time=$(echo $res | cut -d';' -f 6)

                echo "[.] Finished. time:$time, mem:$mem"

                echo "$i $time $mem" >> bench_drs_${benchmark}_${opt_str}_f$f.dat

            done

            echo 
            
        done

    done

done

rm -f $TMPINPUT

# EOF
