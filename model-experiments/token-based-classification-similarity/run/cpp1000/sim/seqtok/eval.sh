#!/bin/bash
#Evaluating Sequence of Tokens similarity analyzer for C++ benchmark dataset
#with 1000 problems with 500 solution source code files each
SRC=../../../../src
python $SRC/PostProcessor/SimSeqTokEvalParall.py ../../tokenize/cpp1000ds --short_code 0 --validation different --valsize 512000 --batch 256 --progress 1 --ckpt_dir sim_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123
