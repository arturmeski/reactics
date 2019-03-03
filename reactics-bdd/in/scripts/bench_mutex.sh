#!/bin/sh

outdir="results"
basefname="mutex_"
forms="`seq 1 3`"
seq_f1="`seq 2 40`"
seq_f2="`seq 2 40`"
seq_f3="`seq 2 40`"

tool="../main"
options="-c -z -v -B"

#ulimit -t 10000
#ulimit -v 2621440

ulimit -t 3600
ulimit -v 2097152

for form in $forms; do
    eval sequence='$'seq_f$form
    for n in $sequence; do
        echo $form $n

    for part in PT MT; do

		echo "$form $n $part"

        if [ "$part" = "PT" ];then
            popt="-x"
            suf="_pt"
        else
            popt=""
            suf=""
        fi

		stopfile="DONE_${basefname}f${form}${suf}.done"

		if [ -e "$stopfile" ];then
			echo "Time limit - SKIPPING"
			continue
		fi

        filename="$outdir/${basefname}${part}_f${form}_n${n}.out"

        echo "$x" > $filename

        ./gen_mutex.py $n $form > tmp.rs

        echo "EXEC: $tool $options $popt tmp.rs"

        $tool $options $popt tmp.rs >&1  >> $filename 

        result="$(tail -1 $filename | grep -E '.*;.*;.*;.*'| sed "s/STAT/$n /")" 
        if [ "$result" = "" ];then
			echo "time limit"
			touch $stopfile
        else
            echo $result >> results/summary_${basefname}${part}_f${form}
            echo $result | sed 's/;/ /g' >> $outdir/${basefname}f${form}${suf}.dat
            echo $result
        fi
    done

    echo
    done
done

