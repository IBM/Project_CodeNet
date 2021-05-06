#!/usr/bin/awk -f

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Expects a C/C++ tokenizer generated CSV file as input.
# (tokenize -m csv)
# Extract all user identifiers.

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
	standard[line]=1
    }
    close(input)
    if (rc < 0)
	print "(W) cannot open " input

    # Add some other standard names:
    # 20
    standard["stdin"]=1
    standard["stdout"]=1
    standard["stderr"]=1
    standard["main"]=1
    standard["argv"]=1
    standard["argc"]=1
    standard["NULL"]=1
    standard["FILE"]=1
    standard["size_t"]=1
    standard["ssize_t"]=1
    standard["int8_t"]=1
    standard["int16_t"]=1
    standard["int32_t"]=1
    standard["int64_t"]=1
    standard["uint8_t"]=1
    standard["uint16_t"]=1
    standard["uint32_t"]=1
    standard["uint64_t"]=1
    standard["uintptr_t"]=1
    standard["errno"]=1

    # Let's throw in some C++ names as well:
    # 11
    standard["std"]=1
    standard["cin"]=1
    standard["cout"]=1
    standard["cerr"]=1
    standard["endl"]=1
    standard["vector"]=1
    standard["map"]=1
    standard["string"]=1
    standard["set"]=1
    standard["queue"]=1
    standard["ptrdiff_t"]=1
    
    # Treat some CPP identifiers as keywords:
    # 10
    standard["include"]=1
    standard["ifdef"]=1
    standard["ifndef"]=1
    standard["elif"]=1
    standard["endif"]=1
    standard["define"]=1
    standard["undef"]=1
    standard["defined"]=1
    standard["__FILE__"]=1
    standard["__LINE__"]=1
    standard["pragma"]=1

    FS=","
    # Skip header:
    getline
}

{
    # Read csv

    # Check for identifier in column 3 (class)
    if ($3 == "identifier")
	if ($4 in standard == 0)
	    print $4
}

END {}
