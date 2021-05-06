#!/usr/bin/awk -f

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Expects a tokenizer generated csv file as input.
# Filters out certain operators and keywords and encodes them
# as numbers in the range [0:16], one per line.

# Hiroki Ohashi, Yutaka Watanobe,
# "Convolutional Neural Network for Classification of Source Codes,"
# 2019 IEEE 13th Int. Symp. on Embedded Multicore/Many-core Systems-on-Chip

BEGIN {

# Assignment operator
    encode["="]=0
    encode["+"]=1
    encode["-"]=1
    encode["*"]=1
    encode["/"]=1
    encode["%"]=1
# Bitwise Operators
    encode["&"]=2
    encode["|"]=2
    encode["^"]=2
    encode["~"]=2
    encode["<<"]=2
    encode[">>"]=2
# Compound arithmetic assignment operators
    encode["+="]=3
    encode["-="]=3
    encode["*="]=3
    encode["/="]=3
    encode["%="]=3
    encode["++"]=3
    encode["--"]=3
# Compound bitwise assignment operators
    encode["&="]=4
    encode["|="]=4
    encode["^="]=4
    encode["<<="]=4
    encode[">>="]=4
# Comparison operators
    encode["=="]=5
    encode["!="]=5
    encode["<"]=5
    encode["<="]=5
    encode[">"]=5
    encode[">="]=5
# Logical operators
    encode["&&"]=6
    encode["||"]=6
    encode["!"]=6
# Others
    encode["if"]=7
    encode["else"]=8
    encode["for"]=9
    encode["while"]=10
    encode["("]=11
    encode[")"]=12
    encode["{"]=13
    encode["}"]=14
    encode["["]=15
    encode["]"]=16

    FS=","
}

{
    # read csv

    # check for operator and keyword in column 3 (class)
    if ($3 == "operator" || $3 == "keyword") {

	# look up field value of column 4 (token)
	if ($4 in encode) {
	    code=encode[$4]

	    #print $4
	    print code
	}
    }
}

END {}
