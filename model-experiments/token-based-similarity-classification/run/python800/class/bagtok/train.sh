#!/bin/bash
#Training Bag of Tokens classifier for python benchmark dataset
#with 800 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
rm -rf class_ckpt
python $SRC/BagOfTokens/BagOfTokensClassifier.py ../../tokenize/python800ds --short_code 0 --dense 128 256 512 --optimizer adam --ckpt_dir class_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123 --history history --epochs $1 --progress 2
