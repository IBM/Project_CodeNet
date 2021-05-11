#!/usr/bin/env bash

if [[ -z "${AI4CODE_HOME}" ]]; 
then
    echo "ENV AI4CODE_HOME must be set"
    echo "do \"source spt.profile\" "
    exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
DEST=0 # if an output directory is set
BATCH=0 # if batch processing is set
COMBINE=0 # if using multiple lexer files to differentiate  token types
die() {
    echo "(E) ${@}" 1>&2
    exit 1
}

for i in "$@"
do
case $i in
    -h|--help)
    echo "Usage: ${SCRIPT_NAME} [-hb] [-d=dir] input_file"
    echo -e "  -b|--batch:\t batch processing"
    echo -e "  -d|--dest:\t path to the SPT and tokens output directory"
    echo -e "  -h|--help:\t show this brief usage summary"

    echo
    echo "When -b option is set, the input_file contains a list of <src_file dest_dir>, no other options should be set."
    echo
    echo "When -b option is not set, -d option must be set, which is the directory where the SPT and tokens write to."
    echo "input_file is the source code to be analyzed."
   
    exit 2
    ;;
    -d=*|--dest=*)
    DEST=1
    OUTPUT_DIR="${i#*=}"
    #echo ${OUTPUT_DIR}
    shift
    ;;
    -b|--batch)
    BATCH=1
    shift
    ;;
    -c|--combine)
    COMBINE=1
    shift
    ;;
  
esac
done

[[ "$#" < 1 ]] && \
  die "Expect as arguments: input_file"
INPUT_FILE="$1"

if [[ $BATCH == 1 ]]; then # batch processing
	[ -d "${OUTPUT_DIR}" ] &&  die "No need to specify output directory (i.e., -d option) in batch processing mode."
	if [[ $COMBINE == 0 ]]; then # use -multi to split tokens
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.SPTGenerator \
			$INPUT_FILE -b -multi
	else
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.SPTGenerator \
			$INPUT_FILE -b 
	fi
else
	[[ $DEST != 1 ]] && \
		die "Single file processing must specify an output directory"
	[ -d "${OUTPUT_DIR}" ] ||  die "Expect output directory ${OUTPUT_DIR}"
	if [[ $COMBINE == 0 ]]; then # use -multi to split tokens
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.SPTGenerator \
		-d ${OUTPUT_DIR} $INPUT_FILE -multi
	else
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.SPTGenerator \
		-d ${OUTPUT_DIR} $INPUT_FILE
	fi
fi

