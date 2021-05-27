#!/bin/bash
#Tokenizing Java benchmark dataset
#with 250 problems with 300 solution source code files each
#Parameters:
# $1  -- path to benchmark dataset with source code files
SRC=../../../src
python $SRC/DSMaker/TokenizeImportDS.py ./java250ds --source $1 --language Java --tok_set Java --update

