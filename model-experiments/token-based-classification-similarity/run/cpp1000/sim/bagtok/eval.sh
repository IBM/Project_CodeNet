#!/bin/bash
#Evaluating Bag of Tokens similarity analyzer for C++ benchmark dataset
#with 1000 problems with 500 solution source code files each
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
python $SRC/BagOfTokens/SimBagTokEval.py ../../tokenize/cpp1000ds --short_code 0 --validation different --batch 256 --progress 1 --testpart 0.2 --valpart 0.2 --seed_ds 123 --valsize 512000 --ckpt_dir sim_ckpt
#foo > allout.txt 2>&1
