#!/bin/bash
#Verification of datsets generated by Sequence of Tokens classifier for Java benchmark dataset
#with 250 problems with 300 solution source code files each
#Parameters:
# $1  -- path to benchmark dataset with source code files
SRC=../../../../src
python $SRC/Verify/ClassDsVerify.py $1 ./dataset_statistics/TestDataset.csv ./dataset_statistics/TrainAndValidDataset.csv



