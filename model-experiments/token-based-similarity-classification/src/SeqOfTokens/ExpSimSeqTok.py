
"""
Experimental program for training source code similarity analyzer
using sequence or Tokens technique by 2-way Siamese type DNN
Uses:
 - experimental Siameze CNN 
 - custom metric
 - class sample weights
runs in multi-GPU mode
History of traing is pickled to be plotted with other application

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code
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

from SeqTok2WaySimDsTF import SeqTok2WaySimDsTF
from ExpSiamModel import ExpSiameseModelFactory
from FuncModelMaker    import *
from ProgramArguments import *
from Utilities import *
from DsUtilities import DataRand

def makeDNN(n_tokens, args):
    """
    Make classification DNN according to program arguments
    Parameters:
    - n_tokens  -- number of token types in the sequences
    - args      -- parsed main program arguments
    """
    _convolutions = list(zip(args.filters, args.kernels, args.strides) 
                         if args.strides
                         else zip(args.filters, args.kernels))
    if args.dnn == "basic":
        _model_factory = FuncModelFactory(
            1, regularizer = (args.l1, args.l2))
        _dnn = _model_factory.siameseSimilarityCNN(
            n_tokens, _convolutions, args.dense,
            pool = args.pool,
            side_dense = args.side_dense,
            conv_act = args.conv_act,
            regul_dense_only = args.regul_dense_only,
            input_type = args.coding,
            dropout_rate = args.dropout,
            merge = args.merge,
            embedding_dim = args.embed,
            optimizer = args.optimizer)
        print("Siamese DNN for similarity analysis is constructed")
    else:
        _model_factory = ExpSiameseModelFactory(
            1, regularizer = (args.l1, args.l2),
            loss = args.loss)
        _dnn = _model_factory.makeCNN(args.dnn,
            n_tokens, _convolutions, args.dense,
            pool = args.pool,
            side_dense = args.side_dense,
            conv_act = args.conv_act,
            regul_dense_only = args.regul_dense_only,
            input_type = args.coding,
            dropout_rate = args.dropout,
            merge = args.merge,
            embedding_dim = args.embed,
            optimizer = args.optimizer)
        print(f"Experimental dnn {args.dnn} is constructed")
    return _dnn

def main(args):
    """
    Main function of program for predicting similarity of 
    two source code samples

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', 
                                                  patience=100)
    #callbacks = [early_stop]
    callbacks = []

    def lrScheduler(epoch, lr):
        """
        Utility function of learning rate scheduler
        Parameters:
        - epoch   -- current epoch
        - lr      -- current learning rate
        Returns new learning rate
        """
        if epoch < 10:
            return lr
        else:
            return lr * tf.math.exp(-0.1)
            
        lrUpdate = \
            tf.keras.callbacks.LearningRateScheduler(
                lrScheduler, verbose=1)

    lrOnPlateaur = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='loss', factor=0.5, patience=2, 
        cooldown=0, min_delta=0.0001, min_lr=0.0001, verbose=1)
    #callbacks.append(lrOnPlateaur)

    if args.ckpt_dir:
        latest_checkpoint = setupCheckpoint(args.ckpt_dir)
        checkpoint_callback = makeCkptCallback(args.ckpt_dir,
                                    monitor = args.monitor)
        callbacks.append(checkpoint_callback)
    else:
        latest_checkpoint = None

    _ds = SeqTok2WaySimDsTF(args.dataset,
            min_n_solutions = args.min_solutions,
            max_n_problems = args.problems,
            short_code_th = args.short_code,
            long_code_th = args.long_code,
            max_seq_length = args.seq_len,
            test = args.testpart,
            batch = args.batch,
            labels01 = not args.symmetric_labels)

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
            print("Restoring from", latest_checkpoint)
            _dnn = tf.keras.models.load_model(latest_checkpoint)
        else:
            print("Constructing DNN")
            _dnn = makeDNN(_ds.n_token_types, args)

    _val_ds, _train_ds = \
        _ds.trainValidDsSameProblems(
            args.valpart, args.valsize, args.trainsize,
            args.similpart) \
        if args.validation == "same" else \
           _ds.trainValidDsDifferentProblems(
               args.valpart, args.valsize, args.trainsize,
               args.similpart)

    _tds = _train_ds[0].prefetch(2)
    _vds = _val_ds[0].prefetch(2)

    if args.sim_weight:
        _w_sim = args.sim_weight / (1.0 + args.sim_weight)
        _w_dissim = 1 - _w_sim
        _class_weight = {-1: _w_dissim, 1: _w_sim} if args.symmetric_labels \
            else {0: _w_dissim, 1: _w_sim}
        history = _dnn.fit(_tds,
                           validation_data = _vds,
                           class_weight = _class_weight,
                           epochs = args.epochs,
                           steps_per_epoch = args.steps_per_epoch,
                           verbose = args.progress,
                           callbacks = callbacks)    
    else:
        history = _dnn.fit(_tds,
                           validation_data = _vds,
                           epochs = args.epochs,
                           steps_per_epoch = args.steps_per_epoch,
                           verbose = args.progress,
                           callbacks = callbacks)

    with open(args.history, 'wb') as _jar:
        pickle.dump(history.history, _jar)
################################################################################
# Args are described below
################################################################################
if __name__ == '__main__':
    print("\nEXPERIMENTAL SOURCE CODE SIMILARITY ANALYZER BY SIAMESE DNN")

    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Experimental source code similarity analysis by Siamese DNN",
        task = "similarity")
    parser = addSeqTokensArgs(parser)
    parser = addRegularizationArgs(parser)
    parser.add_argument("--side_dense", type=int, nargs='*',
                        help="sizes of dense layers")
    parser.add_argument("--merge", type=str, 
                        default="concatenate", 
                        choices=["concatenate", "subtract",
                                 "dot_prod_sigmoid", "cosine"],
                        help="method of merging outputs of siamese blocks of dnn")
    parser.add_argument('--symmetric_labels', action='store_true', 
                        default=False,
                        help="use symmetric labels: -1 and +1")
    parser.add_argument("--sim_weight", default = None, type=float,
                        help = "weight of similar samples")
    parser.add_argument("--steps_per_epoch", default = None, type=int,
                        help = "Steps per training epoch")
    parser.add_argument("--monitor", type=str, 
                        default="val_accuracy", 
                        choices=["val_accuracy", "val_loss"],
                        help="metric to monitor for checkpoints")
    parser.add_argument("--loss", type=str, default=None, 
                        help="loss function to optimize")
    args = parseArguments(parser)
    checkConvolution(args)

    main(args)


