#!/bin/bash
#Evaluation of Bag of Tokens similarity analyzer for Java benchmark dataset
#with 250 problems with 300 solution source code files each
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
python $SRC/BagOfTokens/SimBagTokEval.py ../../tokenize/java250ds --validation different --batch 256 --progress 1 --testpart 0.2 --valpart 0.2 --seed_ds 123 --valsize 512000 --ckpt_dir sim_ckpt
