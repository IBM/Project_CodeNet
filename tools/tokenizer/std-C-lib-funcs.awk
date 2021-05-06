#!/usr/bin/awk -f

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Expects a C tokenizer generated csv file as input.
# Recognizes identifiers and checks them against a list of all standard
# C library functions (from /usr/include header files).
# If the identifier matches, then its token class is modified:
# from "identifier" to "std_func"
# All other tokens are untouched.

function dirname(pathname) {
    if (!sub(/\/[^\/]*\/?$/, "", pathname))
	return "."
    return pathname
}

BEGIN {
    # Read the file of all C standard function names, one per line

    # Get directory where this script resides (ugly hack):
    getline cmdline <("/proc/"PROCINFO["pid"]"/cmdline")
    split(cmdline, fields, "\0")
    path = dirname(fields[3])

    input = path "/std-C-lib-funcs.txt"
    while ((rc = (getline line < input)) > 0) {
	std_funcs[line]=1
    }
    close(input)
    if (rc < 0)
	print "(W) cannot open " input

    FS=","
}

{
    # read csv

    # check for identifier in column 3 (class)
    if ($3 == "identifier" && $4 in std_funcs) {
	# separate out certain identifiers:
	print $1","$2",std_func,"$4
    }
    else {
	print $0
    }
}

END {}
