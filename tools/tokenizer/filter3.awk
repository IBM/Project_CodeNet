#!/usr/bin/awk -f

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Expects a C/C++ tokenizer generated CSV file as input.
# (tokenize -m csv)
# Outputs one possibly modified token (class or literal) per line.
# Recognizes identifiers and checks them against a list of all standard
# C library functions (from /usr/include header files), CPP directives,
# and some other standard names like stdin, stdout, etc.
# Any other identifiers will simply output as the token class name identifier.
# Keywords are output as themselves, i.e., while is output as while.
# Integer and floating-point literals are collectively output as number.
# Character and string literals are output as their class.
# Some operators and punctuation are distinguished; all others output as
# operator.
# Preprocessor symbols are output as # resp. ##.

function dirname(pathname) {
    if (!sub(/\/[^\/]*\/?$/, "", pathname))
	return "."
    return pathname
}

BEGIN {
    # Read the file of all C standard function names, one per line
    # 280

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
    # 11
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

    # 16
    punctuation = "[](){}<>;?::,...="

    FS=","
    # Skip header:
    getline
}

{
    # Read csv

    # Vocabulary size:
    #   5 class names: identifier, number, operator, character, string
    #  95 C/C++20 keywords
    # 280 standard functions
    #  42 cpp and other standard names
    #  16 punctuation symbols
    #   2 preprocessor symbols # and ##
    #   2 integer constants 0,1
    # === +
    # 442

    # Check for identifier in column 3 (class)
    if ($3 == "identifier") {
	# Separate out certain identifiers:
	if ($4 in standard)
	    print $4
	else
	    # Maybe use a shorter identifier representative, like ident or id
	    print $3
    }
    else if ($3 == "operator") {
	# Separate out certain punctuation:
	if (index(punctuation, $4) != 0)
	    print $4
	else
	# Mind the escaped comma "," which is eaten by FS:
	if ($4 == "\"" && $5 == "\"")
	    print ","
	else
	    # Maybe use a real operator; need one that can be used
	    # prefix, infix, and postfix
	    print $3
    }
    else if ($3 == "keyword" || $3 == "preprocessor")
	print $4
    else if ($3 == "integer") {
	# Allow some specific values: 0 and 1
	# (minus sign is not part of number literal!)
	if (index("0 1", $4) != 0)
	    print $4
	else
	    # Maybe use an integer number representative, like 123
	    print "number"
    }
    else if ($3 == "floating")
	# Consolidate integer and floating:
	# Maybe use an integer number representative, like 123
	print "number"
    else # character or string
	# Maybe use a real string "" and char literal 'A'
	print $3
}

END {}
