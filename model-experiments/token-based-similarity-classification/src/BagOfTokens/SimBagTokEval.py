"""
Program for evaluating source code similarity analyzer using
bag or Tokens technique e

For correct evaluation of DNN model it is required that 
the test dataset is generated with the same parameters
"""
import sys
import os
import argparse
import tensorflow as tf

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/BagOfTokens",
                 f"{main_dir}/Dataset",
                 f"{main_dir}/CommonFunctions",
                 f"{main_dir}/PostProcessor"])

from BagTokSimilarityDS import BagTokSimilarityDS
from ProgramArguments import *
from Utilities import *
from DsUtilities import DataRand
from SimilConfusion import SimilConfusAnalysis

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

    _checkpoint = getCheckpoint(args.ckpt_dir, args.ckpt)

    _ds = BagTokSimilarityDS(args.dataset,
                             min_n_solutions = args.min_solutions,
                             max_n_problems = args.problems,
                             short_code_th = args.short_code,
                             long_code_th = args.long_code,
                             test = args.testpart)
    print("Restoring from", _checkpoint)
    _dnn = tf.keras.models.load_model(_checkpoint)
    _test_ds, _labels, _annotations = \
                    _ds.testDataset(args.valsize, args.similpart)
    _eval_loss, _eval_acc = _dnn.evaluate(_test_ds, _labels,
                                          verbose = args.progress)

    _prob = _dnn.predict(_test_ds, verbose = args.progress)
    _confusion = SimilConfusAnalysis(_prob, _labels, 
                                     _ds.solution_names,
                                     _ds.problems, _annotations)
    print("\n")
    print("Evaluation accuracy is {:5.2f}%".format(_eval_acc * 100))
    print("Evaluation loss is {:5.2f}".format(_eval_loss))
    _confusion.writeReport()
##############################################################################
# Args are described below
##############################################################################
if __name__ == '__main__':
    print("\nEVALUATION OF SOURCE CODE SIMILARITY ANALYZER")
    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Evaluation of source code similarity analyzer",
        task = "similarity")
    parser.add_argument("--ckpt", default = None,
                        type=str, help="checkpoint file")
    args = parseArguments(parser)
    main(args)
