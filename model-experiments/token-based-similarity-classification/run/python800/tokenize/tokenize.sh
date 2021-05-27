#!/bin/bash
#Tokenizing python benchmark dataset
#with 800 problems with 300 solution source code files each
#Parameters:
# $1  -- path to benchmark dataset with source code files
SRC=../../../src
python $SRC/DSMaker/TokenizeImportDS.py ./python800ds --source $1 --language python --tok_set python --update

