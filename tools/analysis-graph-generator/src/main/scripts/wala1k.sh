#!/bin/bash

DIR=`dirname $0`
DIR=`realpath $DIR`

lst=$1
dir=$2

shift; shift

hosts="$@"
nodes=${#@}
slices=`expr 15 '*' $nodes`

slice=0
for host in $hosts; do
    ssh $host bash $DIR/wala_node.sh $lst $dir $slice $slices &
    slice=`expr $slice + 15`
done

wait

for f in `ls $dir/11/* | fgrep -v .csv | fgrep -v .txt`; do
    d=`basename $f`
    gawk -f $DIR/to_numbers.awk $dir/*/$d
done

for f in $dir/11/*.csv; do
    stem=`basename $f`
    cat $dir/*/$stem > $dir/$stem
done

gzip $dir/*.csv
