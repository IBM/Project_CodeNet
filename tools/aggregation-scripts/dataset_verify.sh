#!/usr/bin/env bash

# Copyright (c) 2020 International Business Machines Corporation
# Prepared by: Geert Janssen <geert@us.ibm.com>

# Verifies the integrity of the dataset.
# This means that all metadata is consulted to make sure all submissions
# mentioned are indeed present. This an elaborate process and can take
# a while.

# FIXME: Cross-check original problem ids:
# - problem_id all the same in every row of each p?????.csv file
# - same for original_problem_id
# - problem_id part of file name: id p????? -> file p?????.csv
# - problem_id once in problem_list.csv and corresponding original_problem_id
#   on that same row (and no where else)

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
DATA_DIR="/Volume1/AI4CODE/CodeNet_AIZU" # -d option
MODE=all				 # -m option
QUIET=					 # -q option

for i in "$@"
do
case $i in
    -h|--help)
    echo "Usage: ${SCRIPT_NAME} [-hq] [-d=dir] [-m=mode]"
    echo -e "  -d|--data:\tpath to the dataset directory"
    echo -e "  -h|--help:\tshow this brief usage summary"
    echo -e "  -m|--mode:\trun in certain checking mode"
    echo -e "  -q|--quiet:\tsuppress informational messages"
    echo
    echo "Option defaults are (empty means not in effect):"
    echo -e "  -d:\t${DATA_DIR}"
    echo -e "  -m:\t${MODE}"
    echo -e "  -q:\t${QUIET}"
    echo
    echo "Verifies the integrity of the dataset:"
    echo "makes sure that metadata and data correspond."
    echo "The available mode options are: metada, data, or all (default)."
    exit 2
    ;;
    -d=*|--data=*)
    DATA_DIR="${i#*=}"
    shift
    ;;
    -m=*|--mode=*)
    MODE="${i#*=}"
    shift
    ;;
    -q|--quiet)
    QUIET=1
    shift
    ;;
    *)
    break;
    ;;
esac
done
if [[ -n ${1:-""} ]]; then
    warn "trailing non-option arguments are ignored"
fi

# Check for existence of dataset directory:
[ -d "${DATA_DIR}" ] || die "Expect dataset directory ${DATA_DIR}"
# Check for expected sub-directory structure:
for dir in "data" "metadata" "problem_descriptions"; do
    [ -d "${DATA_DIR}/${dir}" ] || die "Expect directory ${DATA_DIR}/${dir}"
done

info "Script '${SCRIPT_NAME}' parameters:"
info "Check mode  : ${MODE}"
info "Dataset dir.: ${DATA_DIR}"

# useful aux vars:
DATA="${DATA_DIR}/data"
METADATA="${DATA_DIR}/metadata"
DESCRIPTIONS="${DATA_DIR}/problem_descriptions"

check_metadata()
{
  # private:
  HEADER="id,name,dataset,time_limit,memory_limit,rating,tags,complexity,original_id,original_contest_id"
  # public:
  #HEADER="id,name,dataset,time_limit,memory_limit,rating,tags,complexity"

  info "Checking problem metadata"

  PROBLEM_CSV="${METADATA}/problem_list.csv"
  # Check if file exists:
  [ -f "${PROBLEM_CSV}" ] || \
      die "missing metadata CSV file ${PROBLEM_CSV}"

  info "Processing ${PROBLEM_CSV}"

  # Assume simple fields, no string quotes, no unnecessary ws, etc
  # The metadata CSV files used to have DOS line endings \r\n !
  {
      read -r header
      # Remove any trailing carriage return:
      header="${header%$'\r'}"
      # Check is header is correct:
      [ "${header}" == "${HEADER}" ] || \
	  warn "incorrect CSV header: ${header}"

      while IFS=, read -a line; do
	# Guaranteed no unnecessary spaces.
	id=${line[0]}

	# Check if problem csv file exists:
	[ -f "${METADATA}/${id}.csv" ] || \
	    warn "missing metadata CSV file for problem ${id}"

	# Check if problem directory exists:
	[ -d "${DATA}/${id}" ] || \
	    warn "missing data directory for problem ${id}"
      done
  } < "${PROBLEM_CSV}"

  # Removed original_user_id
  # private:
  HEADER="submission_id,problem_id,user_id,date,language,original_language,filename_ext,status,cpu_time,memory,code_size,accuracy,original_submission_id,original_problem_id,original_contest_id"
  # public:
  #HEADER="submission_id,problem_id,user_id,date,language,original_language,filename_ext,status,cpu_time,memory,code_size,accuracy"

  info "Checking whether all source files mentioned in metadata exist"

  # Consider all problem metadata CSV files:
  for SUBMISSIONS_CSV in ${METADATA}/p?????.csv; do

    info "Processing ${SUBMISSIONS_CSV}"

    # Get the problem id from the CSV filename:
    problem="${SUBMISSIONS_CSV: -10}"
    problem="${problem:0:6}"

    # Check if problem description exists:
    [ -f "${DESCRIPTIONS}/${problem}.html" ] || \
	warn "missing HTML description for ${problem}"

    # Check if problem directory exists:
    [ -d "${DATA}/${problem}" ] || \
	warn "missing directory for ${problem}"

    # Assume simple fields, no string quotes, no unnecessary ws, etc
    # The metadata CSV files used to have DOS line endings \r\n !
    {
      read -r header
      # Remove any trailing carriage return:
      header="${header%$'\r'}"
      # Check is header is correct:
      [ "${header}" == "${HEADER}" ] || \
	  die "incorrect CSV header: ${header}"

      while IFS=, read -a line; do
	# Guaranteed no unnecessary spaces.
	submission_id=${line[0]}
	problem_id=${line[1]}
	language=${line[4]}
	filename_ext=${line[6]}
	status=${line[7]}

	# Check that status is not empty:
	[ "${status}" != "" ] || \
	    warn "unexpected empty status"
	# Check if metadata CSV file name matches problem id:
	[ "${problem_id}" == "${problem}" ] || \
	    warn "problem filename ${problem} and id ${problem_id} mismatch"
	# Check if language directory exists:
	subdir="${DATA}/${problem_id}/${language}"
	[ -d "${subdir}" ] || \
	    warn "missing directory ${language} for ${problem_id}"
	# Check if submission file exists:
	file="${subdir}/${submission_id}.${filename_ext}"
	[ -f "${file}" ] || \
	    warn "missing submission ${subdir}/${file}"
      done
    } < "${SUBMISSIONS_CSV}"
  done
}

# And now for the reverse check:

check_data()
{
  info "Checking whether all source files are mentioned in the metadata"

  # Process all submission source files in all problem and language dirs:

  # Need this to avoid problems with empty directories:
  shopt -s nullglob

  num_incorrect_code_size=0
  
  # Let's traverse the directories:
  pushd "${DATA}" >/dev/null
  for problem_id in *; do
    info "Processing submissions for problem ${problem_id}"
    # Get the path of this problem_id metadata CSV file:
    csv="${METADATA}/${problem_id}.csv"
    pushd "${problem_id}" >/dev/null
    for language in *; do
      info "Processing submissions for language ${language}"
      pushd "${language}" >/dev/null
      for submission in *; do
	# Note: > 2 million times
	# Get submission_id and ext from filename:
	submission_id="${submission%.*}"
	filename_ext="${submission##*\.}"

	# Try to get submission record in metadata:
	record=$(fgrep "${submission_id}," ${csv})
	if [ $? != 0 ]; then
	    warn "missing submission ${submission} in ${problem_id}.csv metadata"
	    continue
	fi

	# Do some more checks on the record:
	# `expect' is perspective of directory structure;
	# `got' is what we find in the submission record.

	# extract certain fields from CSV record:
	IFS=, read -a line < <(echo "${record}")

	# check problem_id
	[ "${line[1]}" == "${problem_id}" ] || \
	    warn "${problem_id}.csv,${submission_id}: problem id mismatch; expect ${problem_id}, got ${line[1]}"
	# check language
	[ "${line[4]}" == "${language}" ] || \
	    warn "${problem_id}.csv,${submission_id}: language mismatch; expect ${language}, got ${line[4]}"
	# check metadata code_size against actual file size
	#IFS=' ' read -ra wc_out <<< $(wc -c "${submission}")
	#size="${wc_out[0]}"
	#Slow alt: size=$(wc -c < "${submission}")
	#Less portable but faster:
	size=$(stat -c %s "${submission}")
	[ "${line[10]}" == "${size}" ] || \
	    warn "${problem_id}.csv,${submission}: code size mismatch; expect ${size}, got ${line[10]}"
	[ "${line[10]}" == "${size}" ] || ((num_incorrect_code_size++))
	# check whether it's DOS file (\r\n line endings):
	if [ $(head -n1 "${submission}"|cat -e|grep -c -m1 -P '(?<!M-)\^M\$$') == 1 ]; then
	    warn "${problem_id}.csv,${submission}: has DOS line endings"
	fi
      done
      popd >/dev/null
    done
    popd >/dev/null
  done
  popd >/dev/null

  [ "${num_incorrect_code_size}" -gt 0 ] && \
      warn "cases with incorrect code size: ${num_incorrect_code_size}"
}

if [ "${MODE}" == "metadata" ] || [ "${MODE}" == "all" ]; then
    check_metadata
fi
if [ "${MODE}" == "data" ] || [ "${MODE}" == "all" ]; then
    check_data
fi
