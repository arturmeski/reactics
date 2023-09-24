#!/usr/bin/env bash

x_values="`seq 2 20`"
y_values="`seq 2 20`"
z_values="`seq 2 20`"
aut_values="a b"

reactics="$1"
reactics_opts="-z -v -B -c"

input_generator="../../examples/bdd/generators/gen_drs.py"

benchname="sig"
formname="f0"

outdir="results_${benchname}"

if [[ -z "$1" ]]
then
    echo "Usage: $0 <path to reactics>"
    exit 1
fi

if [[ ! -x "$reactics" ]]
then
    echo "Provided path to ReactICS not executable"
fi

if [[ ! -d "$outdir" ]]
then
    echo "Creating output directory: $outdir"
    mkdir -p $outdir
fi

#ulimit -t 3600
#ulimit -v 2097152
ulimit -t 360
ulimit -v 1000000

for a in $aut_values
do
    for x in $x_values
    do
        for y in $y_values
        do
            for z in $z_values
            do

                if [[ $y -lt $z ]]
                then
                    # Skip undesired values
                    continue
                fi

                bench_identifier="${benchname}_F${formname}_A${a}"

                filename_base="${outdir}/${benchname}_F${formname}__x${x}_y${y}_z${z}_A${a}" 
                outfile="${filename_base}.out"
                infile="${filename_base}.drs"

		stopfile="DONE_${bench_identifier}"

                if [[ -e "$stopfile" ]]
                then
                    echo "Time limit -- SKIPPING"
                    continue
                fi

                $input_generator $x $y $z $a > ${infile}

                $reactics $reactics_opts $formname $infile > ${outfile} 2>&1 
                exitcode=$?
                echo "ReactICS exit code: $exitcode"

                result="$(tail -1 $outfile | grep -E '.*;.*;.*;.*'| sed "s/STAT/$n /")" 
                if [ "$result" = "" ]
                then
                    echo "TIME LIMIT; marking as finished"
                    touch $stopfile
                else
                    echo "$x ; $y ; $z ; $a ; $exitcode $result" >> $outdir/summary_${bench_identifier}.txt
                    echo "$x $y $z $a $(echo $result | sed 's/;/ /g')" >> $outdir/${bench_identifier}.dat
                    echo $result
                fi

            done
        done
    done
done

# EOF
