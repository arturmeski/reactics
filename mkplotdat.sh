#!/bin/sh
if [ "$1" = "" ];then
	echo "Usage: $0 <input file>"
	exit 1
fi
f="$1"
cat $f | tr -d '()' | tr ',' '\t'

