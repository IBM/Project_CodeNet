#!/usr/bin/env bash

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

USAGE="\
Expects a C, C++, or Java source file as input and extracts all\n\
function definitions reachable from a given start function name\n\
(by default \"main\"). Uses srcml and xmlstarlet to do the parsing and\n\
ML processing. Note that only functions are output; any other\n\
top-level definitions and declarations are lost!"

# The abolute directory path where this script resides:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

. "${SCRIPT_DIR}"/callgraph_aux.sh

info "Outputting reachable function definitions..."

# Test for presence of a function definition (true or false):
#xidel -s -e 'boolean(//function[name="comment"])' test1.xml 

# Get the source text of a function (assuming presence):
#xidel -s -e '//function[name="comment"]' test1.xml 

# Function names (1 per line) in reverse DFS order:
for ((n=next_num-1;n>=0;n--)); do
    func="${dfs_name[$n]}"
    # Is there a function definition present?
    result=$(xidel -s -e "boolean(//function[name=\"${func}\"])" $XML)
    if [ "${result}" = "true" ]; then
	# Output the source text:
	echo
	xidel -s -e "//function[name=\"${func}\"]" $XML
    fi
done
