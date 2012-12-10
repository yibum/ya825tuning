#!/bin/sh

filename=$1
n=$3

tmpfile=~/Library/Caches/tmp.out

for lineind in `seq 1 935`
do
	esind=$(( ($lineind-1)*${n} ))
	for sind in `seq 1 ${n}`
	do
		sed -n $(( ${esind}+${sind} ))p $1 | awk '{split($0, a, " |,"); print a[3]}' >> $tmpfile
	done
	paste -sd+ $tmpfile | bc >> $2 && rm $tmpfile
done