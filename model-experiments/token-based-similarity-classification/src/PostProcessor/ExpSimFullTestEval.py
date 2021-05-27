"""
Experimental program for complete evaluation of similarity analyzer 
using sequence or Tokens technique by 2-way siamese type DNN
Program analyzes all pairs of source code samples
Program operated in in multi-GPU mode
Uses:
 - experimental Siameze CNN 
 - custom metric
"""
import sys
import os
import argparse
import pickle
import tensorflow as tf

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset",
                 f"{main_dir}/CommonFunctions",
                 f"{main_dir}/PostProcess",
                 f"{main_dir}/ModelMaker"])

from SeqTokSim2WayComplDS import SeqTokSim2WayComplDS
from ProgramArguments import parseArguments
from Utilities import *
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
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    latest_checkpoint = getCheckpoint(args.ckpt_dir, args.ckpt)

    _ds = SeqTokSim2WayComplDS(args.dataset,
                               short_code_th = 1,
                               max_seq_length = args.seq_len,
                               seq_len_to_pad = args.pad_len,
                               labels01 = not args.symmetric_labels)
    #Indices of problems corresponding to subsequences of samples
    _sample_probl_indices = _ds.sample_probl_indices
    with open(f"{args.out_dir}/problem_indices.pcl", "wb") as _f:
        pickle.dump(_sample_probl_indices, _f)

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
        if args.loss:
            _loss = getLossFunction(args.loss)
            with tf.keras.utils.custom_object_scope({'loss_function': _loss}):
                _dnn = tf.keras.models.load_model(latest_checkpoint)
        else:
            _dnn = tf.keras.models.load_model(latest_checkpoint)
    _test_ds = _ds.testDataset(batch = args.batch)
    if args.evaluate:
        _eval_loss, _eval_acc = _dnn.evaluate(_test_ds, verbose = args.progress)
        print("\n")
        print("Evaluation accuracy is {:5.2f}%".format(_eval_acc * 100))
        print("Evaluation loss is {:5.2f}".format(_eval_loss))
    _prob = _dnn.predict(_test_ds, verbose = args.progress)
    _prob = _prob[:,0]
    with open(f"{args.out_dir}/similarity_probabilities.pcl", "wb") as _f:
        pickle.dump(_prob, _f)
    """
    _confusion = SimilConfusAnalysis(_prob, _labels, 
                                     _ds.solution_names,
                                     _ds.problems, _annotations)
    """

    #_confusion.writeReport()
##############################################################################
# Args are described below
##############################################################################
if __name__ == '__main__':
    print("\nEVALUATION OF SOURCE CODE SIMILARITY ANALYZER")
    #Handle command-line arguments
    parser = argparse.ArgumentParser(description = 
                "Evaluation of source code similarity analyzer")
    parser.add_argument("dataset",
                        type=str, help="dataset directory")
    parser.add_argument("ckpt_dir",
                        type=str, help="checkpoint directory")
    parser.add_argument("out_dir",
                        type=str, help="directory for results")
    parser.add_argument("--ckpt", default = None,
                        type=str, help="checkpoint file")
    parser.add_argument("--batch", default=32, type=int,
                        help="batch size")
    parser.add_argument('--seq_len', default=None, type=int,
                        help='maximum lengths of token sequence')
    parser.add_argument('--pad_len', default=None, type=int,
                        help='sequence lengths to pad to')
    parser.add_argument('--symmetric_labels', action='store_true', 
                        default=False,
                        help="use symmetric labels: -1 and +1")
    parser.add_argument("--loss", type=str, default=None, 
                        help="loss function to optimize")
    parser.add_argument('--evaluate', action='store_true', 
                        default=False,
                        help="run evaluation")
    parser.add_argument('--progress', default=2, type=int,
                        choices=[0, 1, 2],
                        help="mode of keras training progress bar")
    args = parseArguments(parser)
    main(args)


