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
    echo -e "  -d|--dest:\t path to the .csv output directory"
    echo -e "  -h|--help:\t show this brief usage summary"

    echo
    echo "When -b option is set, the input_file contains a list of <src_file dest_dir>, no other options should be set."
    echo
    echo "When -b option is not set, the input_file is the source code to be analyzed."
    echo "When -d option is set, dir is the directory where the token file (.csv) outputs to. When -d option is not set, tokens will be written to stdout."
    
   
    exit 2
    ;;
    -d=*|--dest=*)
    DEST=1
    OUTPUT_DIR="${i#*=}"
    echo ${OUTPUT_DIR}
    shift
    ;;
    -b|--batch)
    BATCH=1
    shift
    ;;
  
esac
done

[[ "$#" < 1 ]] && \
  die "Expect as arguments: input_file"
INPUT_FILE="$1"
if [[ $DEST == 1 ]]; then
	# Check for existence of output directory:
	[ -d "${OUTPUT_DIR}" ] || die "Expect output directory ${OUTPUT_DIR}"
	# single file output to output_dir
	java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.Tokenizer --multi \
	-d ${OUTPUT_DIR} $INPUT_FILE  
else
	if [[ $BATCH == 1 ]]; then # batch processing
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.Tokenizer --multi \
		$INPUT_FILE -b
	else # single file output to stdout
		java -cp ${external_jar_path}:${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar com.ibm.ai4code.parser.Tokenizer --multi \
		$INPUT_FILE
	fi	
fi  

