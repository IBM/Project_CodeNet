#!/usr/bin/awk -f

# Copyright (c) 2021 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Expects a C/C++ tokenizer generated CSV file as input with explicit
# whitespace and separate newline (and continuation) tokens.
# (tokenize -W -n [-N] -mcsv)
# Outputs one possibly modified token (class or literal) per line.
# Tries to use some context to better discriminate the meaning of some
# otherwise ambiguous tokens.

# Should use yacc/bison or lemon?

# Ambiguous tokens in C/C++:
# < > delimiters of filename in preprocessor include directive
# < > delimiters of template parameters
# < less than operator
# > greater than operator
# " " delimiters of filename in preprocessor include directive
# " " delimiters of string literal
# ( ) expression grouping
# ( ) argument list
# { } block
# { } initializer
# [ ] indexing
# [ ] lambda capture
# ~ destructor
# ~ unary operator
# - unary operator
# - binary operator
# * unary operator
# * binary operator
# * pointer declarator

# Simplistic CPP line syntax:
# "#" directive-name (token)* newline

# #include <sys.h>
# #include "local"
# #define identifier-macro-def
# #define identifier-macro-const val
# #define identifier-macro-func( ... )

# Using a stack to remember CSV token lines whose output is temporarily
# suppressed. That way can have unbounded lookahead.
# Use function to empty and print stack from bottom to top.

function push(record) {
    stack[sp++]=record
}

function empty_out() {
    for (i=0; i<sp; i++)
	print stack[i]
    sp=0
}

BEGIN {
    # CPP directive-names:
    directive["include"]=1
    directive["define"]=1
    directive["undef"]=1
    directive["if"]=1
    directive["ifdef"]=1
    directive["ifndef"]=1
    directive["else"]=1
    directive["elif"]=1
    directive["endif"]=1
    directive["line"]=1
    directive["pragma"]=1
    directive["error"]=1

    # Empty stack of tokens:
    sp=0
    # Start (current) state:
    state=0
    # Next state:
    next_state=-1 # indicates no specific rule matches
    # Field separator of input record (line):
    FS=","
    # Read CSV header line:
    getline
    # Echo to output:
    print #0
}

# Note: only gawk has switch statement.

# Dispatch on current state and input.
# Make sure all conditions are mutually exclusive, except last one.
# Last one is made exclusive by next_state==-1.
# Must use next_state to avoid immediate action on current line.


# Instead of composing new CSV record could also modify $0 via
# assignments to its fields (like $3="identifier").

# A # followed by an identifier in a macro body means stringize the identifier.
(state == 0 && $4 == "#") {
    push($0)
    next_state=1
}

# # seen; expect directive or identifier.
(state == 1 && $3 == "identifier") {
    push($0)
    if ($4 in directive) {
	if ($4 == "include")
	    next_state=2
	else
	if ($4 == "define")
	    next_state=7
	else {
	    empty_out()
	    next_state=0
	}
    }
    else { # #ident => stringize to "ident"
	empty_out()
	next_state=0
    }
}

# Handle #include <...
(state == 2 && $4 == "<") {
    # Note: suppressing this token.
    next_state=3
}

# Handle #include "...".
(state == 2 && $3 == "string") {
    # $4 has enclosing " doubled!
    filename=substr($4,3,length($4)-4)
    empty_out()
    print $1 "," $2 ",string-local-filename," filename
    next_state=0
}

# (state == 2 && anything else) => default action.

# Collect all tokens after the < till >.
# Treat first (assume its an identifier) specially to get its coordinates.
(state == 3 && $3 == "identifier") {
    id_lin=$1
    id_col=$2
    filename=$4
    # Note: modifying this token.
    next_state=4
}

# Keep collecting tokens till >.
(state == 4 && $4 != ">") {
    filename=filename $4
    # Note: suppressing this token.
    next_state=4
}

# Seen #include <...>.
(state == 4 && $4 == ">") {
    empty_out()
    print id_lin "," id_col ",string-sys-filename,\"" filename "\""
    # Note: suppressing this token.
    next_state=0
}

# states 5, 6 not used for now.

# Handle #define name.
(state == 7 && $3 == "identifier") {
    id_lin=$1
    id_col=$2
    macro_name=$4
    # Note: modifying this token.
    next_state=8
}

# Handle #define name(.
(state == 8 && $4 == "(") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-func," macro_name
    print $0
    next_state=0
}

# Handle #define name (.
(state == 8 && $3 == "whitespace") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-const," macro_name
    next_state=0
}

# Handle #define name.
(state == 8 && $3 != "whitespace" && $4 != "(") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-def," macro_name

    if ($4 == "#") { # With -n should never happen.
	push($0)
	next_state=1
    }
    else { # Most probably a newline.
	print $0
	next_state=0
    }
}

# Default rule; always executed.
{
    if (next_state == -1) {
	# Echo all other tokens as is (ignore whitespace though):
	if ($3 != "whitespace")
	    print $0
	# Do not change state!
    }
    else {
	state=next_state
	next_state=-1
    }
}

END {}
