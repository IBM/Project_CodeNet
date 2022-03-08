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
# Resolved by using preceding #include context
# < > delimiters of template parameters
# < less than operator
# Resolve: preceding context keyword template, template <+
# > greater than operator
# Resolve: preceding context keyword template <
# " " delimiters of filename in preprocessor include directive
# " " delimiters of string literal
# Resolved by using preceding #include context
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
# Resolve: no white-space after - then unary?
# * unary operator (dereference pointer)
# * binary operator (multiplication)
# * pointer declarator
# & bitwise and operator
# & address of operator
# Can of worms: overloaded operator symbols

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
# All rules when matched must set next_state to something other than -1.

# Instead of composing new CSV record could also modify $0 via
# assignments to its fields (like $3="identifier").

# A # followed by an identifier in a macro body means stringize the identifier.
(state == 0 && $4 == "#") {
    push($0)
    next_state=1
}

# The keyword template provides context for some < and > disambiguation.
(state == 0 && $4 == "template") {
    print $0
    next_state=0 # switched off for now
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

# Collect all tokens after the < till >.
# Treat first specially to get its coordinates.
(state == 3 && ($3 == "identifier" || $3 == "keyword")) {
    id_lin=$1
    id_col=$2
    filename=$4
    # Note: modifying this token.
    next_state=4
}

# Keep collecting tokens till > or newline.
(state == 4 && $3 != "newline" && $4 != ">") { # eats up anything
    filename=filename $4
    # Note: suppressing this token.
    next_state=4
}

# Handling #include <...>, or #include <...newline.
(state == 4 && ($3 == "newline" || $4 == ">")) {
    # When newline it's an error, but act as if > was present:
    empty_out()
    print id_lin "," id_col ",string-sys-filename,\"" filename "\""
    if ($3 == "newline")
	print $0
    # else suppressing the > token.
    next_state=0
}

# Handle template <.
(state == 5 && $4 == "<") {
    $3="start-template-paramlist"
    print $0
    next_state=6
}

# Handle template < >, explicit specialization.
(state == 6 && $4 == ">") {
    $3="end-template-paramlist"
    print $0
    next_state=0
}

# Handle #define name.
(state == 7 && ($3 == "identifier" || $3 == "keyword")) {
    id_lin=$1
    id_col=$2
    macro_name=$4
    # Note: modifying this token later.
    next_state=8
}

# Handle #define name(.
(state == 8 && $4 == "(") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-func," macro_name
    print $0
    next_state=0
}

# Handle #define name whitespace
(state == 8 && $3 == "whitespace") {
    # Note: suppressing this token.
    next_state=9
}

# Handle #define name whitespace? newline
((state == 8 || state == 9) && $3 == "newline") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-def," macro_name
    print $0
    next_state=0
}

# Handle #define name whitespace !newline.
(state == 9 && $3 != "newline") {
    empty_out()
    print id_lin "," id_col ",identifier-macro-const," macro_name
    print $0
    next_state=0
}

# Default rule; always executed:
# 1. no prior rule matched:
#    - stay in same state only for whitespace, newline, and continuation;
#      this allows for their presence without explicit mention in rules
#    - output any previously suppressed tokens (to not lose them)
#    - print current token except for whitespace
#    - back to state 0 to quickly recover for any errors in input
# 2. some rule matched:
#    - simply move on to next state as stated in that rule
#    - reset next_state to -1
{
    if (next_state == -1) {
	# Echo the current token as is (ignore whitespace though):
	if ($3 != "whitespace") {
	    if ($3 != "newline" && $3 != "continuation") {
		empty_out()
		state=0
	    }
	    print $0
	}
	# otherwise: Do not change state!
    }
    else {
	state=next_state
	next_state=-1
    }
}

END {}
