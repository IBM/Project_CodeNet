#!/bin/bash
#Evaluating contest testset with DNN source code similarity analyzer:
#Parameters:
# $1  -- directory with source code files
# $2  -- csv file with sample pairs to analyze
# $3  -- csv file with ground truth labels
DATA=$1
TEST=$2
TOKENIZER=/Volume1/AI4CODE/bin/tokenize
DNN=dnn_ckpt
if test $# -gt 2; then
    echo "Evaluating DNN accuracy on test set"
    python TestSetEval.py $DATA $TEST --labels $3 --tokenizer $TOKENIZER --dnn $DNN --predictions ./predictions_2.csv --batch 400
fi
echo "Computing predictions of source code similarity"
python TestSetEval.py $DATA $TEST --tokenizer $TOKENIZER --dnn $DNN --predictions ./predictions_1.csv --batch 400
