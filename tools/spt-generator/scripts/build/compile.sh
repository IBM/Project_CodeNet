#!/usr/bin/env bash
if [[ -z "${AI4CODE_HOME}" ]]; 
then
    echo "ENV AI4CODE_HOME must be set"
    echo "You can set AI4CODE_HOME by"
    echo "source spt.profile"
    exit 1
fi



# step 1 compile SPT related classes
rm -fr ${AI4CODE_HOME}/classes
mkdir -p ${AI4CODE_HOME}/classes
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/commons/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/c/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/c_multi/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/cpp/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/cpp_multi/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/python/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/python_multi/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/java/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/java_multi/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/cymbol/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/cymbol_multi/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/cobol/*.java -d ${AI4CODE_HOME}/classes/
javac ${javacflags} -cp ${external_jar_path}:${AI4CODE_HOME}/classes/  ${AI4CODE_HOME}/src/com/ibm/ai4code/parser/*.java -d ${AI4CODE_HOME}/classes/
mkdir -p ${AI4CODE_HOME}/targets
jar cf ${AI4CODE_HOME}/targets/ibm-ai4code-v0.1.jar -C ${AI4CODE_HOME}/classes .
