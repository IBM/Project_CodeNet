"""
Program for code classification by Sequence or Tokens technique
using convolutional neural network in multi-GPU mode

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
import tensorflow as tf

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset",
                 f"{main_dir}/ModelMaker",
                 f"{main_dir}/CommonFunctions"])

from ProgramArguments  import *
from Utilities         import *
from DsUtilities       import DataRand
from SeqTokDataset     import SeqTokDataset
from SeqModelMaker     import SeqModelFactory
from ExperimentalModel import ExperimentModelFactory
from ModelUtils        import UniqueSeed

def makeDNN(n_tokens, n_labels, args):
    """
    Make classification DNN according to program arguments
    Parameters:
    - n_tokens  -- number of token types in the sequences
    - n_labels  -- number of class lables
    - args      -- parsed main program arguments
    """
    _convolutions = \
            list(zip(args.filters, args.kernels, args.strides) 
                 if args.strides
                 else zip(args.filters, args.kernels))
    if args.dnn == "basic":
        _model_factory = SeqModelFactory(n_tokens, n_labels)
        _dnn = _model_factory.cnnDNN(_convolutions, args.dense,
                                     pool = args.pool,
                                     conv_act = args.conv_act,
                                     regular = (args.l1, args.l2),
                                     regul_dense_only = args.regul_dense_only,
                                     input_type = args.coding,
                                     dropout_rate = args.dropout,
                                     optimizer = args.optimizer, 
                                     embedding_dim = args.embed)
        print("Basic dnn for source code classification is constructed")
    else:
        _model_factory = ExperimentModelFactory(n_labels,
                                                regularizer = (args.l1, args.l2))
        _dnn = _model_factory.doublePoolClassCNN(
            n_tokens,
            _convolutions, args.dense,
            conv_act = args.conv_act,
            input_type = args.coding,
            embedding_dim = args.embed,
            regul_dense_only = args.regul_dense_only,
            dropout_rate = args.dropout,
            optimizer = args.optimizer)
        print("Experimental dnn with both max and average pooling is constructed")
    return _dnn

def main(args):
    """
    Main function of program for classifying source code

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    UniqueSeed.setSeed(args.seed_model)

    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', 
                                                  patience=args.patience)
    callbacks = [early_stop]
    if args.ckpt_dir:
        latest_checkpoint = setupCheckpoint(args.ckpt_dir)
        checkpoint_callback = makeCkptCallback(args.ckpt_dir)
        callbacks.append(checkpoint_callback)
    else:
        latest_checkpoint = None

    _ds = SeqTokDataset(args.dataset,
                        min_n_solutions = max(args.min_solutions, 3),
                        max_n_problems = args.problems,
                        short_code_th = args.short_code,
                        long_code_th = args.long_code,
                        max_seq_length = args.seq_len,
                        test_part = args.testpart,
                        balanced_split = args.balanced_split)

    print(f"Classification of source code among {_ds.n_labels} classes")
    print("Technique of convolutional neural network on sequence of tokens\n")
    #Create parallelization strategy for multi GPU mode
    #It also can be either MirroredStrategy or MultiWorkerMirroredStrategy
    #But MultiWorkerMirroredStrategy works better
    strategy = tf.distribute.MultiWorkerMirroredStrategy()
    #distribute.MirroredStrategy()
    print("Number of devices: {}".format(strategy.num_replicas_in_sync))  
    #Construct DNN in the scope of parrelization strategy.
    with strategy.scope():
        # Everything that creates variables should be under the strategy scope.
        # In general this is only model construction & `compile()`.
        if latest_checkpoint:
            print("Restoring DNN from", latest_checkpoint)
            _dnn = tf.keras.models.load_model(latest_checkpoint)
        else:
            print("Constructing DNN")
            _dnn = makeDNN(_ds.n_token_types, _ds.n_labels, args)
    _val_ds, _train_ds = _ds.trainValidDs(args.valpart, args.batch)

    _tds = _train_ds[0]
    _tds = _tds.shuffle(50, reshuffle_each_iteration=True,
                        seed = UniqueSeed.getSeed()).prefetch(2)

    history = _dnn.fit(_tds,
                       validation_data = _val_ds[0].prefetch(2),
                       epochs = args.epochs, verbose = args.progress,
                       callbacks = callbacks)
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
