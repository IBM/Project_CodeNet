
"""
Experimental program for evaluation of source code similarity analyzer 
using sequence or Tokens technique by 2-way Siamese type DNN
Uses:
 - experimental Siameze CNN 
 - custom metric
runs in multi-GPU mode

For correct evaluation of DNN model it is required that the test datset is 
generated with the same parameters
"""
import sys
import os
import argparse
import tensorflow as tf
from tensorflow import keras

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/SeqOfTokens",
                 f"{main_dir}/Dataset",
                 f"{main_dir}/CommonFunctions",
                 f"{main_dir}/PostProcess",
                 f"{main_dir}/ModelMaker"])

from SeqTok2WaySimDsTF import SeqTok2WaySimDsTF
from ProgramArguments import *
from Utilities import *
from DsUtilities import DataRand
from SimilConfusion import SimilConfusAnalysis
from ExpSiamModel import (getLossFunction,
                          relaxedCrossEntropy, sinCrossEntropy,
                          cappedCrossEntropy)

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

    latest_checkpoint = getCheckpoint(args.ckpt_dir, args.ckpt)

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
    #Construct DNN in the scope of parallelization strategy.
    with strategy.scope():
        # Everything that creates variables should be under the strategy scope.
        # In general this is only model construction & `compile()`.
        print("Restoring from", latest_checkpoint)
        #with tf.keras.utils.custom_object_scope({}):
        if args.loss:
            _loss = getLossFunction(args.loss)
            with tf.keras.utils.custom_object_scope({'loss_function': _loss}):
                _dnn = tf.keras.models.load_model(latest_checkpoint)
        else:
            _dnn = tf.keras.models.load_model(latest_checkpoint)
    _test_ds, _labels, _annotations = \
                    _ds.testDataset(args.valsize, args.similpart)
    _eval_loss, _eval_acc = _dnn.evaluate(_test_ds, 
                                          verbose = args.progress)

    _prob = _dnn.predict(_test_ds, verbose = args.progress)
    _confusion = SimilConfusAnalysis(_prob, _labels, 
                                     _ds.solution_names,
                                     _ds.problems, _annotations,
                                     labels01 = not args.symmetric_labels)
    print("\n")
    print("Evaluation accuracy is {:5.2f}%".format(_eval_acc * 100))
    print("Evaluation loss is {:5.2f}".format(_eval_loss))
    _confusion.writeReport()
##############################################################################
# Args are described below
##############################################################################
if __name__ == '__main__':
    print("\nEVALUATION OF EXPERIMENTAL SOURCE CODE SIMILARITY ANALYZER")
    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Evaluation of source code similarity analyzer",
        task = "similarity")
    parser.add_argument("--ckpt", default = None,
                        type=str, help="checkpoint file")
    parser.add_argument('--seq_len', default=None, type=int,
                        help='maximum lengths of token sequence')
    parser.add_argument('--symmetric_labels', action='store_true', 
                        default=False,
                        help="use symmetric labels: -1 and +1")
    parser.add_argument("--loss", type=str, default=None, 
                        help="loss function to optimize")
    args = parseArguments(parser)
    main(args)


