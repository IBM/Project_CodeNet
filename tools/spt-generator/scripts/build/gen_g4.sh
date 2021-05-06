#!/usr/bin/env bash
if [[ -z "${AI4CODE_HOME}" ]]; 
then
    echo "ENV AI4CODE_HOME must be set"
    echo "You can set AI4CODE_HOME by"
    echo "source spt.profile"
    exit 1
fi

gen() {
	lang=$1
	work_dir=${AI4CODE_HOME}/src/com/ibm/ai4code/parser/$lang
	package_name="com.ibm.ai4code.parser.$lang"
	echo $work_dir
	echo $package_name
	pushd $work_dir
	java org.antlr.v4.Tool *.g4 -package $package_name
	popd
}

gen c
gen c_multi
gen cpp
gen cpp_multi
gen java
gen java_multi
gen python
gen python_multi
gen cymbol
gen cymbol_multi
gen cobol