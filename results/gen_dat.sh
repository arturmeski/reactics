#!/bin/sh

for logfile in *.log; do

    log_base_name=$(basename -s .log $logfile)
    dat_output="${log_base_name}.dat"
    cut -d, -f 1,3 $logfile | tr -d '()' | tr ',' '\t' > $dat_output

done
