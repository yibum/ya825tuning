#!/bin/sh


lineind=1
filedir=$1
echo $filedir
for filename in $filedir
do
	echo "Extracting line $lineind, $filename"
	extension="${filename##*.}"
	outfile="${filename%.*}.l${lineind}.${extension}"

	#head -1 $filename > ${outfile}
done