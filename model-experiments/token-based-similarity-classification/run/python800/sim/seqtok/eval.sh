#!/bin/bash
#Evaluating Sequence of Tokens similarity analyzer for python benchmark dataset
#with 800 problems with 300 solution source code files each
SRC=../../../../src
python $SRC/PostProcessor/SimSeqTokEvalParall.py ../../tokenize/python800ds --short_code 0 --validation different --valsize 512000 --batch 256 --progress 1 --ckpt_dir sim_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123
