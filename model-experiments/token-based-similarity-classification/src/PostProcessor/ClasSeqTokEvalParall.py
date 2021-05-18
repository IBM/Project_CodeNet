"""
Program for evaluation of source code classifier using
sequence or Tokens technique by 2-way siamese type DNN in multi-GPU mode

For correct evaluation of DNN model it is required that the test datset is 
generated with the same parameters
"""
import sys
import os
import argparse
import tensorflow as tf

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/SeqOfTokens",
                 f"{main_dir}/Dataset",
                 f"{main_dir}/CommonFunctions",
                 f"{main_dir}/PostProcess"])

from SeqTokDataset    import SeqTokDataset
from DsUtilities      import DataRand
from ProgramArguments import *
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
    
    latest_checkpoint = getCheckpoint(args.ckpt_dir, args.ckpt)

    _ds = SeqTokDataset(args.dataset,
                        min_n_solutions = max(args.min_solutions, 3),
                        max_n_problems = args.problems,
                        short_code_th = args.short_code,
                        long_code_th = args.long_code,
                        max_seq_length = args.seq_len,
                        test_part = args.testpart,
                        balanced_split = args.balanced_split)

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
        _dnn = tf.keras.models.load_model(latest_checkpoint)
    _test_ds, _labels, _sample_names, _label_names = \
                                _ds.testDS(args.batch)
    _eval_loss, _eval_acc = _dnn.evaluate(_test_ds, 
                                  verbose = args.progress)
    _prob = _dnn.predict(_test_ds, verbose = args.progress)
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
                        type=str, help="checkpoint file")
    parser.add_argument('--seq_len', default=None, type=int,
                        help='maximum lengths of token sequence')
    args = parseArguments(parser)
    main(args)


