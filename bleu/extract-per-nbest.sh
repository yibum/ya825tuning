#!/bin/sh
# usage: ./extract-per-nbest.sh NBestList dst_dir N

filename=$1
dst_dir=$2
n=$3
mkdir -p $dst_dir
for lineind in `seq 1 935`
do
	cutline_start=$(( (lineind-1)*n+1 ))
	cutline_end=$(( cutline_start+9 ))
	#echo $cutline_start, $cutline_end
	outfile="${dst_dir}/nbest.l${lineind}"
	for cutlineind in `seq ${cutline_start} ${cutline_end}`
	do
		echo $lineind, $cutlineind
		sed -n ${cutlineind}p $filename \
		| awk '{split($0, a, "|"); print a[4]}' >> $outfile
	done
done