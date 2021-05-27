#!/bin/bash
#Training Sequence of Tokens classifier for C++ benchmark dataset
#with 1400 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf class_ckpt
python $SRC/SeqOfTokens/SeqClassParallel.py ../../tokenize/cpp1400ds --short_code 0 --kernels 15 5 1 --filters 1024 512 320 --conv_act relu --dense 320 1536 --coding trainable --embed 48 --optimizer adam --epochs $1 --batch 512 --ckpt ./class_ckpt --l2 0.00002 --dropout 0.1 --testpart 0.2 --valpart 0.2 --l1 0.0000000015 --seed_ds 123 --progress 2



