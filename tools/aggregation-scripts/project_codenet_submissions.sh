#!/usr/bin/env bash

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Extract all source code submissions for
# - a given problem id, p12345
# - a certain programming language, Java
# - a particular status, Accepted
# - a minimum code size in bytes, 0
# - a maximum code size in bytes, unlimited
# - how many samples to provide, all available
# using metadata in per problem .csv file.
# Assumes dataset has been verified for integrity.
# No elaborate checks in inner loop.

# The abolute directory path where this script resides:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

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

# Directory that is the root all data and metadata:
DATA_DIR="/Volume1/AI4CODE/CodeNet"      # -d option
AMOUNT=					 # -n option
QUIET=					 # -q option
SUPPRESS=				 # -s option

for i in "$@"
do
case $i in
    -h|--help)
    echo "Usage: ${SCRIPT_NAME} [-hqs] [-n=amount] [-d=dir] problem_id [language [status [min_size [max_size]]]]"
    echo -e "  -d|--data:\t path to the root of the dataset directory"
    echo -e "  -h|--help:\t show this brief usage summary"
    echo -e "  -n|--amount:\t amount of submissions to provide"
    echo -e "  -q|--quiet:\t be quiet; no informational messages"
    echo -e "  -s|--suppress: suppress the directory path on output"
    echo
    echo "Option defaults are (empty means not in effect):"
    echo -e "  -d:\t${DATA_DIR}"
    echo -e "  -n:\t${AMOUNT}"
    echo -e "  -q:\t${QUIET}"
    echo -e "  -s:\t${SUPPRESS}"
    echo
    echo "Outputs a list of filenames for the requested submissions."
    echo "There are 1000s of problem ids, too many to list here."
    echo "A problem id follows the pattern p[0-9]{5}."
    echo "There are 55 available languages, but not all problems have"
    echo "submissions for each. Some popular ones are:"
    echo "  C (default), C#, C++, D, Go, Haskell, Java, JavaScript,"
    echo "  Kotlin, OCaml, PHP, Python, Ruby, Rust, and Scala."
    echo "The possible values for status are:"
    echo -e '  "Compile Error"'
    echo -e '  "Wrong Answer"'
    echo -e '  "Time Limit Exceeded"'
    echo -e '  "Memory Limit Exceeded"'
    echo -e '  "Accepted" (default)'
    echo -e '  "Judge Not Available"'
    echo -e '  "Output Limit Exceeded"'
    echo -e '  "Runtime Error"'
    echo -e '  "WA: Presentation Error"'
    echo "min_size is 0 by default and max_size is unlimited."
    echo "The bounds are inclusive."
    exit 2
    ;;
    -n=*|--amount=*)
    AMOUNT="${i#*=}"
    shift
    ;;
    -d=*|--data=*)
    DATA_DIR="${i#*=}"
    shift
    ;;
    -q|--quiet)
    QUIET=1
    shift
    ;;
    -s|--suppress)
    SUPPRESS=1
    shift
    ;;
esac
done

[[ "$#" < 1 ]] && \
  die "Expect as arguments: id [language (C) [status (Accepted) [min_size (0) [max_size (unlimited)]]]]"

# Check for existence of dataset directory:
[ -d "${DATA_DIR}" ] || die "Expect dataset directory ${DATA_DIR}"
# Check for expected sub-directory structure:
for dir in "data" "metadata" "problem_descriptions"; do
    [ -d "${DATA_DIR}/${dir}" ] || die "Expect directory ${DATA_DIR}/${dir}"
done

# useful aux vars:
DATA="${DATA_DIR}/data"
METADATA="${DATA_DIR}/metadata"
DESCRIPTIONS="${DATA_DIR}/problem_descriptions"

PROBLEM_ID="$1"
LANGUAGE="${2:-C}"
STATUS="${3:-Accepted}"
MIN_CODE_SIZE="${4:-0}"
MAX_CODE_SIZE="${5}"

info "Script '${SCRIPT_NAME}' parameters:"
info "Problem id: ${PROBLEM_ID}"
info "Language  : ${LANGUAGE}"
info "Status    : ${STATUS}"
info "Min size  : ${MIN_CODE_SIZE}"
info "Max size  : ${MAX_CODE_SIZE:-"unlimited"}"
info "Amount    : ${AMOUNT:-"all available"}"
info "Data dir. : ${DATA_DIR}"

# Directory of this problem id:
PROBLEM_DIR="${DATA}/${PROBLEM_ID}"

# Check for existence of problem directory:
[ -d "${PROBLEM_DIR}" ] || die "Expect problem directory ${PROBLEM_DIR}"

# Problem CSV metadata file:
SUBMISSIONS_CSV="${METADATA}/${PROBLEM_ID}.csv"

# Check for existence:
[ -f "${SUBMISSIONS_CSV}" ] || die "Expect to read ${SUBMISSIONS_CSV}"

# Check size bounds:
if [ "${MAX_CODE_SIZE}" ]; then
    [ "${MIN_CODE_SIZE}" -le "${MAX_CODE_SIZE}" ] || \
	die "must have min_size (${MIN_CODE_SIZE}) <= max_size (${MAX_CODE_SIZE})"
fi

#private:
#HEADER="submission_id,problem_id,user_id,date,language,original_language,filename_ext,status,cpu_time,memory,code_size,accuracy,original_submission_id,original_user_id,original_problem_id,original_contest_id"

#public:
HEADER="submission_id,problem_id,user_id,date,language,original_language,filename_ext,status,cpu_time,memory,code_size,accuracy"

# Full path to submission file is optional:
[ -n ${SUPPRESS:-""} ] && FP="" || FP="${PROBLEM_DIR}/${LANGUAGE}/"

# Extract all submissions from the CSV matadata:
info "Processing ${SUBMISSIONS_CSV}"

SAMPLES=0

# Assume simple fields, no string quotes, no unnecessary ws, etc
# The metadata CSV files might have DOS line endings \r\n !
{
    read -r header
    # Remove any trailing carriage return:
    header="${header%$'\r'}"
    # Check is header is correct:
#    [ "${header}" == "${HEADER}" ] || die "unexpected CSV header: ${header}"

    while IFS=, read -a line; do
	# Guaranteed no unnecessary spaces.
	language="${line[4]}"

	# Select on language:
	[ "${LANGUAGE}" != "${language}" ] && continue

	# Select on status:
	status="${line[7]}"
	[ "${STATUS}" != "${status}" ] && continue

	# Get submission filename:
	submission_id="${line[0]}"
	filename_ext="${line[6]}"
	file="${FP}${submission_id}.${filename_ext}"

	# Select on true file size (which is assumed to be correct):
	size="${line[10]}"
	#size=$(wc -c < "${file}")
	#Less portable but faster:
	#size=$(stat -c %s "${file}")
	[ "${size}" -lt "${MIN_CODE_SIZE}" ] && continue
	[ "${MAX_CODE_SIZE}" ] && [ "${size}" -gt "${MAX_CODE_SIZE}" ] && \
	    continue

	[ "${AMOUNT}" ] && [ "${SAMPLES}" -ge "${AMOUNT}" ] && exit 0

	# Output submission filename [path]:
	printf "${file}\n"

	((SAMPLES++))
    done
} < "${SUBMISSIONS_CSV}"

[ "${AMOUNT}" ] && [ "${SAMPLES}" -lt "${AMOUNT}" ] && \
    warn "selection (${PROBLEM_ID},${LANGUAGE},${STATUS}) has ${SAMPLES} out of requested ${AMOUNT} submissions"
