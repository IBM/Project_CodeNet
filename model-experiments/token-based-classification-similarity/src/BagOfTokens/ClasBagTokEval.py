"""
Program for evaluating source code classifier using
bag or Tokens technique 

For correct evaluation of DNN model it is required 
that the test datset is  generated with the same parameters
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
from BagTokDataset    import BagTokDataset
from DsUtilities      import DataRand
from ProgramArguments import (makeArgParserCodeML, parseArguments)
from Utilities        import *
from ClassConfusion   import ClassConfusAnalysis

def main(args):
    """
    Main function of program for classifying source code samples
    and evaluating its accuracy

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    
    _checkpoint = getCheckpoint(args.ckpt_dir, args.ckpt)

    _ds = BagTokDataset(args.dataset,
                        min_n_solutions = max(args.min_solutions, 3),
                        max_n_problems = args.problems,
                        short_code_th = args.short_code,
                        long_code_th = args.long_code,
                        test_part = args.testpart,
                        balanced_split = args.balanced_split)

    print("Restoring from", _checkpoint)
    _dnn = tf.keras.models.load_model(_checkpoint)

    _test_ds, _labels, _sample_names, _label_names = \
                                _ds.testDS(args.batch)
    _eval_loss, _eval_acc = _dnn.evaluate(_test_ds[0], _test_ds[1],
                                  verbose = args.progress)
    _prob = _dnn.predict(_test_ds[0], verbose = args.progress)
    _confusion = ClassConfusAnalysis(_prob, _labels, _sample_names,
                                     _label_names)
    _confusion.writeReport()
    print("\n")
    print("Evaluation accuracy is {:5.2f}%".format(_eval_acc * 100))
    print("Evaluation loss is {:5.2f}".format(_eval_loss))
################################################################################
# Args are described below
################################################################################
if __name__ == '__main__':
    print("\nEVALUATION OF SOURCE CODE CLASSIFIER")
    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Evaluation of source code classifier",
        task = "classification")
    parser.add_argument("--ckpt", default = None,
                        type=str, help="checkpoint file to load")
    args = parseArguments(parser)

    main(args)
