#!/usr/bin/env bash

# Showcasing the use of tokml and xidel.
# Works for any Java, C, and C++ source file.
# Extracts certain tokens and statistics of interest.

# Show command and execute it.
run() {
  echo "$ $1"
  eval "$1"
  [ $? == 0 ] || die "got non-0 program exit code"
}

die() {
    echo "(E) ${@}" 1>&2
    exit 1
}

# We need an input file:                                                      
[ -z "$1" ] && die "expect a C, C++, or Java file as argument"

# Quick check for availabilty of tokml and xidel:
command -v tokml &>/dev/null
[ $? == 0 ] || die "tokml not available; please install"
command -v xidel &>/dev/null
[ $? == 0 ] || die "xidel not available; please install"

# Create temp file:
XML="$(mktemp /tmp/${1%.*}-XXX.xml)"
# Ensure clean up when done:
trap "/bin/rm -f $XML" EXIT
echo \# Run tokml to obtain the .xml output file:
run "tokml $1 > $XML"

echo
echo \# Count the number of tokens in the arg source file:
run "xidel -s -e 'count(//source/*)' $XML"

echo
echo \# Show all unique identifiers \(sorted\):
run "xidel -s -e '//identifier' $XML | sort | uniq"

echo
echo \# Show the identifier occurrences of length greater than 10:
run "xidel -s -e '//identifier[@len>10]' $XML"

echo
echo \# How many block_comment occurrences are there?
run "xidel -s -e 'count(//block_comment)' $XML"

echo
echo \# Which tokens immediately follow the keyword static?
run "xidel -s -e '//keyword[text()=\"static\"]/following-sibling::*[1]' $XML | sort | uniq"

echo
echo \# What is the value of the first integer number?
run "xidel -s -e '//integer[1]' $XML"

echo
echo \# Convert the XML back to the original source and show 20 lines:
run "xidel -s -e 'source' $XML | head -n20"
