#!/bin/bash
#!/bin/bash
#Evaluating Sequence of Tokens classifier for Java benchmark dataset
#with 250 problems with 300 solution source code files each
SRC=../../../../src
python $SRC/PostProcessor/ClasSeqTokEvalParall.py ../../tokenize/java250ds --short_code 0 --batch 256 --progress 1 --ckpt_dir class_ckpt --testpart 0.2 --valpart 0.2 --seed_ds 123
