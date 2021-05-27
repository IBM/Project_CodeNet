#!/bin/bash
#Evaluation of Sequence of Tokens similarity analyzer for Java benchmark dataset
#with 250 problems with 300 solution source code files each
SRC=../../../../src
python $SRC/PostProcessor/SimSeqTokEvalParall.py ../../tokenize/java250ds --validation different --valsize 512000 --batch 256 --progress 1 --ckpt_dir sim_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123
