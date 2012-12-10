#!/bin/sh
# usage: ./extract-n-lines.sh source_dir dst_dir
# total 993 lines in each ref, get from "wc -l *.ref.en[0-10]"
filedir=$1
for lineind in `seq 1 935`
do
# extract each corresponding to each file
dst_filedir=${2}/l$lineind
mkdir -p $dst_filedir
for path_filename in ${filedir}/*
do
	echo "Extracting line $lineind, $path_filename"

	filename=$(basename "$path_filename")
	extension="${filename##*.}"
	outfile="${dst_filedir}/${filename%.*}.l${lineind}.${extension}"
	echo "Writing to ${outfile}"
	sed -n "${lineind}p" $path_filename > ${outfile}
done

done