DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export AI4CODE_HOME=$DIR
export CLASSPATH=".:${AI4CODE_HOME}/resources/antlr-4.8-complete.jar"
export external_jar_path="${AI4CODE_HOME}/resources/antlr-4.8-complete.jar:${AI4CODE_HOME}/resources/commons-csv-1.8.jar:${AI4CODE_HOME}/resources/commons-cli-1.4.jar"
export javacflags="-Xlint:deprecation"
function antlr4 { # note alias only works in interactive shell, so we need to make a function defintion before we can call it in another shell
	 java org.antlr.v4.Tool $1
}

