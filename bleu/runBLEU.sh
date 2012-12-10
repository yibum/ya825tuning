#!/bin/sh
# usage: ./runBLEU.sh ref_dir nbest_list_dir n
# -lc means lowercase

n=$3
ref_dir=$1
filename_pre="mt_chinese_p3.ref"
filename_ext="en" # multi references

bleu_path=~/Workspace/Misc/tools/mosesdecoder/scripts/generic/multi-bleu.perl

tmpfile=~/Library/Caches/atmp.out
outfile=~/Library/Caches/bleu_none.out

for lineind in `seq 1 935` #935 is the total number of lines
do
	ref_per_line_dir=${ref_dir}/l${lineind}
	per_line_refs=${ref_per_line_dir}/${filename_pre}.l${lineind}.${filename_ext}
	nbest_file=${2}/nbest.l${lineind}
	for candidate in `seq 1 ${n}`
	do
		echo $lineind, $candidate
		sed -n "${candidate}p" < ${nbest_file} > ${tmpfile} && \
		${bleu_path} -lc ${per_line_refs} < ${tmpfile} >> ${outfile}
	done
done