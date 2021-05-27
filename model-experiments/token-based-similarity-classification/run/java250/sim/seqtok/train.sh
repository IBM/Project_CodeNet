#!/bin/bash
#Training Sequence of Tokens similarity analyzer for Java benchmark dataset
#with 250 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf sim_ckpt
python $SRC/SeqOfTokens/SimSeqTokParallel.py ../../tokenize/java250ds --short_code 0 --coding trainable --embed 64 --kernels 17 5 1 --filters 512 256 256 --validation different --epochs $1 --steps_per_epoch 200 --dense 256 128 --conv_act relu --optimizer adam --trainsize 20480000 --valsize 512000 --batch 256 --dropout 0.1 --ckpt sim_ckpt --merge subtract --regul_dense_only --l2 0.000005 --l1 0.000000001 --testpart 0.2 --valpart 0.2 --seed_ds 123 --progress 2
