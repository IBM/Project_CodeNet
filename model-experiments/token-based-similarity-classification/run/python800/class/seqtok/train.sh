#!/bin/bash
#Training Sequence of Tokens classifier for python benchmark dataset
#with 800 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf class_ckpt
python $SRC/SeqOfTokens/SeqClassParallel.py ../../tokenize/python800ds --short_code 0 --kernels 19 5 1 --filters 512 256 256 --conv_act relu --dense 256 512 960 --coding trainable --embed 64 --optimizer adam --epochs $1 --batch 512 --ckpt ./class_ckpt --l2 0.00005 --dropout 0.1 --testpart 0.2 --valpart 0.2 --l1 0.000000001 --seed_ds 123 --progress 2



