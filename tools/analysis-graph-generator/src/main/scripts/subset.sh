#!/bin/bash

DIR=`dirname $0`
DIR=`realpath $DIR`

dir=$1
graphs=$2
out_dir=$3

nodes=`gzcat $dir/num-node-list.csv.gz | gawk -v graphs=${graphs} 'BEGIN {N=0;} NR<=graphs {N+=$1} END { print N }'`

edges=`gzcat $dir/num-edge-list.csv.gz | gawk -v graphs=${graphs} 'BEGIN {N=0;} NR<=graphs {N+=$1} END { print N }'`

for f in num-edge-list.csv.gz num-node-list.csv.gz graph-label.csv.gz; do
    gzcat $dir/$f | awk -v g=${graphs} 'NR<=g { print $0; }' | gzip > $out_dir/$f
done

for f in edge.csv.gz; do
    gzcat $dir/$f | awk -v e=${edges} 'NR<=e { print $0; }' | gzip > $out_dir/$f
done

for f in node_dfs_order.csv.gz node_is_attributed.csv.gz node-feat.csv.gz node_depth.csv.gz; do
    gzcat $dir/$f | awk -v n=${nodes} 'NR<=n { print $0; }' | gzip > $out_dir/$f
done



