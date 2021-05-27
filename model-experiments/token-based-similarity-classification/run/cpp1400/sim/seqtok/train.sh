#!/bin/bash
#Training Sequence of Tokens similarity analyzer for C++ benchmark dataset
#with 1400 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf class_ckpt
python $SRC/SeqOfTokens/SimSeqTokParallel.py ../../tokenize/cpp1400ds --short_code 0 --coding trainable --embed 32  --kernels 15 5 1 --filters 256 160 128 --validation different --epochs $1 --steps_per_epoch 250 --dense 128 128 --conv_act relu --optimizer adam --trainsize 10000000 --valsize 400000 --batch 256 --dropout 0.15 --ckpt sim_ckpt --merge subtract --regul_dense_only --l2 0.000005 --l1 0.000000001 --testpart 0.2 --valpart 0.2 --seed_ds 123 --progress 2
