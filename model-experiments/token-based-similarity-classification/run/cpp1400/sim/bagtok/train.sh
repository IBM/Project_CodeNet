#!/bin/bash
#Training Bag of Tokens similarity analyzer for C++ benchmark dataset
#with 1400 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
export CUDA_VISIBLE_DEVICES=0
SRC=../../../../src
rm -rf sim_ckpt
python $SRC/BagOfTokens/SimilarityByBoT.py ../../tokenize/cpp1400ds --short_code 0  --dense 64 32 4 --validation different --testpart 0.2 --valpart 0.2 --seed_ds 123 --trainsize 4096000 --valsize 512000 --ckpt_dir sim_ckpt  --batch 256 --epochs $1 --progress 2
