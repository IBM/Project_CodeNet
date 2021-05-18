"""
Program for code classification by Sequence or Tokens technique
using convolutional neural network

History of traing is pickled to be plotted with other application

Implements convolutional neural network classifier of 
sorce code represented with sequeence of tokens
Its number of convolutional and dense layers, 
and their dimensions are specified by program arguments.

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code

Number of classes (lables) is defined automatically

Program arguments are defined below in definition of 
argparse Argmuments Parser object
"""
import sys
import os
import argparse
import pickle
import numpy as np
import tensorflow as tf
import random as python_random

main_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.extend([f"{main_dir}/../Dataset",
                 f"{main_dir}/../ModelMaker",
                 f"{main_dir}/../PostProcessor",
                 f"{main_dir}/../CommonFunctions"])

from Utilities        import resetSeeds
from ProgramArguments import (makeArgParserCodeML, parseArguments, 
                              addSeqTokensArgs, addRegularizationArgs,
                              checkConvolution)
from SeqTokDataset    import SeqTokDataset
from DsUtilities      import DataRand
from SeqModelMaker    import SeqModelFactory
from ClassConfusion   import ClassConfusAnalysis

def confusionAnalysis(dnn, ds, labels, solutions, problems):
    """
    Perform confusion analysis and report its results
    Parameters:
    - dnn       -- DNN to make classification
    - ds        -- Dataset to classify
    - labels    -- Labels as indices of classes
    - solutions -- Names of problem solutions (names of samples)
    - problems  -- Names of problems (names of classes)
    """
    _prob = dnn.predict(ds)
    _confusion = ClassConfusAnalysis(_prob, labels, solutions, 
                                     problems)
    _confusion.writeReport()

def train(dnn, val_ds, train_ds, epochs,
          history_fn, verbose):
    """
    Train given DNN on given dataset

    - dnn            -- DNN compiled and optimized
    - val_ds         -- Valdiation dataset as a pair 
                        of sample and lables arrays
    - train_ds       -- Training dataset as as a pair 
                        of sample and lables arrays
    - epochs         -- Number of training epochs
    - history_fn     -- Name of file to pickle training history
    - verbose        -- Keras mode of verbosity: 0, 1, 2
    """
    history = dnn.fit(train_ds,
                      epochs = epochs,
                      validation_data = val_ds,
                      verbose = verbose)
    with open(history_fn, 'wb') as _jar:
        pickle.dump(history.history, _jar)

def main(args):
    """
    Main function of program for classifying source code

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    
    _ds = SeqTokDataset(args.dataset,
                        min_n_solutions = max(args.min_solutions, 3),
                        max_n_problems = args.problems,
                        short_code_th = args.short_code,
                        long_code_th = args.long_code,
                        max_seq_length = args.seq_len,
                        balanced_split = args.balanced_split)

    print(f"Classification of source code among {_ds.n_labels} classes")
    print("Technique of convolutional neural network on sequence of tokens\n")
    _model_factory = SeqModelFactory(_ds.n_token_types, _ds.n_labels)
    _convolutions = list(zip(args.filters, args.kernels, args.strides) 
                         if args.strides
                         else zip(args.filters, args.kernels))
    _dnn = _model_factory.cnnDNN(_convolutions, args.dense,
                                 pool = args.pool,
                                 conv_act = args.conv_act,
                                 regular = (args.l1, args.l2),
                                 input_type = args.coding,
                                 optimizer = args.optimizer, 
                                 embedding_dim = args.embed)

    _val_ds, _train_ds = _ds.trainValidDs(args.valpart, args.batch)

    train(_dnn, _val_ds[0], _train_ds[0], args.epochs,
          args.history, args.progress)
    _ds, _labels, _sample_names, _label_names = _val_ds
    confusionAnalysis(_dnn, _ds,  _labels, _sample_names, _label_names)

#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nCODE CLASSIFICATION WITH SEQUENCE OF TOKENS TECHNIQUE")

    #Command-line arguments
    parser = makeArgParserCodeML(
        "Sequence of tokens source code classifier",
        task = "classification")
    parser = addSeqTokensArgs(parser)
    parser = addRegularizationArgs(parser)
    args = parseArguments(parser)

    checkConvolution(args)

    main(args)
