#!/usr/bin/env bash

# Copyright (c) 2021 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Post-process duplicates output to create a graph
# Only applies to Project CodeNet
# File names are assumed to be absolute.
# Assumes submissions are ordered by problem id.

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

PROGRESS=0             # show progress spinner
FILES=0                # number of files mentioned
SETS=0                 # number of duplicate file sets
SETSIZE=0	       # determines the size of a set
SINGLETONS=0	       # number of singleton clusters
CUR_PROBLEM=	       # current problem id

if [ "${PROGRESS}" -eq 1 ]; then
    i=1
    sp='/-\|.'
fi

declare -A problem_submissions
declare -A problem_singletons
declare -A problem_clusters
declare -A adjacency
declare -A clusters
declare -A incremented

# Read stdin or a file mentioned on as command-line argument:
while read LINE; do

    # Reset on a blank line; next line will be a first file of a set.
    if [ -z "${LINE}" ]; then
        #echo "end of cluster"
	# Count singleton sets:
	if [ ${SETSIZE} -eq 1 ]; then
	    # Another singleton for this problem:
	    ((problem_singletons[${problem_id}]++))
	    ((SINGLETONS++))
	    #((adjacency[$problem_id]--))
	fi
	# Indicate start of fresh cluster:
        SETSIZE=0
	unset incremented
	declare -A incremented
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
    path="${LINE%%:*}"
    dir="${path%/*}"
    submission="${path##*/}"
    language="${dir##*/}"
    dir="${dir%/*}"

    problem_id="${dir##*/}"
    #echo "${dir}|${problem_id}|${language}|${submission}"

    if [ ${SETSIZE} -eq 0 ]; then
        #echo "start of a new cluster for ${problem_id}"
        ((SETS++))
	if [ -z "${CUR_PROBLEM}" ]; then
	    # First time only.
	    CUR_PROBLEM="${problem_id}"
	else
	    # Check for change in problem.
	    if [ "${problem_id}" != "${CUR_PROBLEM}" ]; then
		# Output all data for previous problem:
		files=$((problem_submissions[${CUR_PROBLEM}]))
		singles=$((problem_singletons[${CUR_PROBLEM}]))
		seen=$((files - adjacency[${CUR_PROBLEM}]))
		echo -n "${CUR_PROBLEM} ${files} ${singles}"
		adjacency[${CUR_PROBLEM}]=$((files-singles-seen))
		for id in "${!adjacency[@]}"; do
		    printf " %s %u %u" "$id" "${clusters[${id}]}" "${adjacency[${id}]}"
		done
		echo
		# Reset:
		unset adjacency
		declare -A adjacency		
		unset clusters
		declare -A clusters
		CUR_PROBLEM="${problem_id}"
	    fi
	fi
	# Another cluster for this problem_id:
	((problem_clusters[$problem_id]++))
    fi
    # Another file that belongs to the cluster for this problem_id:
    ((adjacency[$problem_id]++))
    # Is this the first mention of this problen in this cluster?
    # For every cluster you may increment once per problem
    if [ -z ${incremented[$problem_id]} ]; then
	((clusters[$problem_id]++))
	((incremented[$problem_id]++))
    fi
    ((problem_submissions[$problem_id]++))
    ((SETSIZE++))

    #echo "${LINE}"
done < "${1:-/dev/stdin}"

# Output all data for last problem:
files=$((problem_submissions[${CUR_PROBLEM}]))
singles=$((problem_singletons[${CUR_PROBLEM}]))
seen=$((files - adjacency[${CUR_PROBLEM}]))
echo -n "${CUR_PROBLEM} ${files} ${singles}"
adjacency[${CUR_PROBLEM}]=$((files-singles-seen))
for id in "${!adjacency[@]}"; do
    printf " %s %u %u" "$id" "${clusters[${id}]}" "${adjacency[${id}]}"
done
echo

#printf "\n"
printf "Number of singletons: %7u\n" "${SINGLETONS}" 1>&2
printf "Number of clusters  : %7u\n" "${SETS}" 1>&2
printf "Number of files     : %7u\n" "${FILES}" 1>&2
# Number of clusters and total files per problem_id:
printf "Problem: #Clusters: #Files: #Singles:\n" 1>&2
for id in "${!problem_clusters[@]}"; do
    printf "%7s, %9u, %6u, %8u\n" \
	   "$id" "${problem_clusters[${id}]}" "${problem_submissions[${id}]}" \
	   "${problem_singletons[${id}]}" 1>&2
done
