#!/bin/bash
#Evaluating Bag of Tokens classifier for C++ benchmark dataset
#with 1400 problems with 300 solution source code files each
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
python $SRC/BagOfTokens/ClasBagTokEval.py ../../tokenize/cpp1400ds --short_code 0 --batch 256 --progress 1 --ckpt_dir class_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123
