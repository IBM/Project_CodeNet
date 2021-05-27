#!/bin/bash
#Training Bag of Tokens classifier for Java benchmark dataset
#with 250 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
rm -rf class_ckpt
python $SRC/BagOfTokens/BagOfTokensClassifier.py ../../tokenize/java250ds --dense 128 160 256 --optimizer adam --short_code 0 --ckpt_dir class_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123 --history history --epochs $1 --progress 2
