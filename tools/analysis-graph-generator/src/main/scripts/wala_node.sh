#!/bin/bash

DIR=`dirname $0`
DIR=`realpath $DIR`

lst=$1
dir=$2
start_slice=$3
slices=$4

for i in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14; do
    (nohup bash -v $DIR/run.sh $lst `expr $i + $start_slice` $slices $dir &)
done

wait
