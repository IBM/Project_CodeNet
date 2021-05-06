#!/usr/bin/env bash

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Post-process fdupes (or jdupes) output.
# A set of duplicate files is presented 1 per line and the sets are
# separated by a blank line. There are at least 2 files per set.
# File names are assumed to be absolute.
# Idea derived from jdupes/example_scripts/example.sh.

die() {
    echo "(E) ${@}" 1>&2
    exit 1
}

warn() {
    echo "(W) ${@}" 1>&2
}

info() {
    # Be quiet when unset or not "":
    [ -n ${QUIET:-""} ] || echo "(I) ${@}" 1>&2
}

PROGRESS=1             # show progress spinner
FILES=0                # number of files mentioned
SETS=0                 # number of duplicate file sets
INCONSIST=0            # number of sets with a mix of languages
ACCEPTED=0             # number of files that are Accepted submissions
LANGUAGE=              # the language of the first file of a set
SETSIZE=0	       # determines the size of a set
ACCEPT_IN_SET=0	       # count of Accepted in current set
ACCEPT_DUPLICATES=0    # sets with 2 or more Accepted submissions

if [ "${PROGRESS}" -eq 1 ]; then
    i=1
    sp='/-\|.'
fi

# Read stdin or a file mentioned on as command-line argument:
while read LINE; do

    # Reset on a blank line; next line will be a first file of a set.
    if [ -z "${LINE}" ]; then
        #echo "end of group"
	if [ ${ACCEPT_IN_SET} -ge 2 ]; then
	    ((ACCEPT_DUPLICATES++))
	fi
        SETSIZE=0
	ACCEPT_IN_SET=0
        continue
    fi

    # Count each file mentioned:
    ((FILES++))

    # Show progress spinner:
    if [ "${PROGRESS}" -eq 1 ]; then
        [ $(($i % 1000)) -eq 0 ] && printf "."
        printf "\b${sp:i++%${#sp}:1}"
    fi
    
    # Extract items from path .../data/problem_id/language/submission:
    dirpath="${LINE%/*}"
    submission="${LINE##*/}"
    language="${dirpath##*/}"
    dirpath="${dirpath%/*}"
    problem_id="${dirpath##*/}"
    dirpath="${dirpath%/*}"
    dirpath="${dirpath%/*}"
    metadata="${dirpath}/metadata"
    #echo "${dirpath}|data|${problem_id}|${language}|${submission}"

    # Get this problem_id metadata CSV file:
    csv="${metadata}/${problem_id}.csv"
    if [ ! -f "${csv}" ]; then
        warn "no such metadata file ${csv}"
        continue
    fi

    # Get submission_id from submission filename:
    submission_id="${submission%.*}"
    # Try to get submission record in metadata:
    record=$(fgrep "${submission_id}," "${csv}")
    if [ $? != 0 ]; then
        warn "missing submission ${submission} in ${problem_id}.csv metadata"
        continue
    fi
    # Extract certain fields from CSV record:
    IFS=, read -a fields < <(echo "${record}")
    
    # Count how many files have Accepted status:
    if [ "${fields[7]}" == "Accepted" ]; then
        ((ACCEPTED++))
        # An Accepted submission better be of the correct language:
	# Already covered by integrity check in dataset_verify.sh.
	# Count how many in a set are Accepted:
	((ACCEPT_IN_SET++))
    fi

    if [ ${SETSIZE} -eq 0 ]; then
        #echo "start of a new group"
        ((SETS++))
        LANGUAGE="${language}"
        SETSIZE=1
    else
        # Set has all same language?
        if [ "${language}" != "${LANGUAGE}" ]; then
            ((INCONSIST++))
        fi
	((SETSIZE++))
    fi

    #echo "${LINE}"
done < "${1:-/dev/stdin}"

printf "\n"
printf "Number of duplicate sets  : %7u\n" "${SETS}"
printf "Number of mixed lang. sets: %7u\n" "${INCONSIST}"
printf "Sets with >=2 Accepted    : %7u\n" "${ACCEPT_DUPLICATES}"
printf "Number of files in sets   : %7u\n" "${FILES}"
printf "Number of Accepted files  : %7u\n" "${ACCEPTED}"
