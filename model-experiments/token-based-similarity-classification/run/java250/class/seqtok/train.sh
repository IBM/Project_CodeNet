#!/bin/bash
#Training Sequence of Tokens classifier for Java benchmark dataset
#with 250 problems with 300 solution source code files each
#Parameters:
#$1 -- number of training epochs to run
SRC=../../../../src
rm -rf class_ckpt
python $SRC/SeqOfTokens/SeqClassParallel.py ../../tokenize/java250ds --short_code 0 --kernels 17 5 1 --filters 512 256 256 --conv_act relu --dense 256 256 320 --coding trainable --embed 64 --optimizer adam --epochs $1 --batch 200 --ckpt ./class_ckpt --l2 0.000025 --dropout 0.1 --testpart 0.2 --valpart 0.2 --l1 0.000000002 --seed_ds 123 --progress 2



