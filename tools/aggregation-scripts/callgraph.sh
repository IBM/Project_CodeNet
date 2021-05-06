#!/usr/bin/env bash

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

USAGE="\
Approximates a call graph using srcml and xmlstarlet.\n\
Works for any C, C++, and possibly Java source file.\n\
Output is in JSON-Graph format. Includes multiplicity.\n\
Note that preprocessor macros (#define) are not resolved;\n\
so even macro calls will be treated as regular function calls."

# The abolute directory path where this script resides:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

. "${SCRIPT_DIR}"/callgraph_aux.sh

info "Outputting in JSON-Graph format..."

# JSON-Graph 'prelude':
echo -e "{\n  \"graph\": {"
echo    "    \"version\": \"1.0\","
echo    "    \"type\": \"dag\","
echo    "    \"directed\": true,"
echo    "    \"root\": 0,"
echo    "    \"order\": \"dfs\","
echo    "    \"label\": \"call graph\","

# The nodes (in DFS order!):
echo    "    \"nodes\": ["
for ((n=0;n<next_num;n++)); do
    caller=${dfs_name[$n]}
    echo -n "      { \"id\": $n, \"label\": \"$caller\" }"
    ((n < next_num-1)) && echo ","
done
echo
echo    "    ],"

# The edges (per node in order of lexical occurrence):
echo    "    \"edges\": ["
first_time=1
for caller in ${!graph[@]}; do
    for callee in ${graph[$caller]}; do
	[ $first_time -eq 1 ] && first_time=0 || echo ","
	echo -n "      { \"between\": "
	echo -n "[ ${dfs_num[$caller]}, ${dfs_num[$callee]} ], "
	echo -n "\"multiplicity\": ${multi[$caller,$callee]}, "
	echo -n "\"relation\": \"calls\" }"
    done
done
echo
echo -e "    ]\n  }\n}"
