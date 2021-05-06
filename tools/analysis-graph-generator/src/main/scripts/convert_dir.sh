#!/bin/bash

DIR=`dirname $0`
DIR=`realpath $DIR`

out_dir=$1

shift

dirs="$@"

mkdir -p $out_dir

for dir in $dirs; do
    for f in $dir/[a-z]*; do
	echo $f
	cat $f >> $out_dir/`basename $f`
    done
done

for f in `ls $out_dir/* | fgrep -v .csv | fgrep -v .txt`; do
    d=`basename $f`
    gawk -f $DIR/to_numbers.awk $f
done

#gzip $out_dir/*.csv
