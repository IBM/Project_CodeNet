#!/bin/bash
#Tokenizing C++ benchmark dataset
#with 1400 problems with 300 solution source code files each
#Parameters:
# $1  -- path to benchmark dataset with source code files
SRC=../../../src
python $SRC/DSMaker/TokenizeImportDS.py ./cpp1400ds --source $1 --language C++ --tok_set CPP56X --update --no_macro

