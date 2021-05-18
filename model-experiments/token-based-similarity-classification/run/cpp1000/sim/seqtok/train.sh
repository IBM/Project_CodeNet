#!/bin/bash
#Training Sequence of Tokens similarity analyzer for C++ benchmark dataset
#with 1000 problems with 500 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf class_ckpt
python $SRC/SeqOfTokens/SimSeqTokParallel.py ../../tokenize/cpp1000ds --short_code 0 --coding trainable --embed 32  --kernels 15 5 1 --filters 320 256 160 --validation different --epochs $1 --steps_per_epoch $1 --dense 160 128 64 --conv_act relu --optimizer adam --trainsize 40000000 --valsize 409600 --batch 256 --dropout 0.15 --ckpt sim_ckpt --merge subtract --regul_dense_only --l2 0.000005 --l1 0.000000001 --testpart 0.2 --valpart 0.2 --seed_ds 123 --progress 2
