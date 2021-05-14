"""
Program for code classification by Bag or Tokens technique

History of traing is pickled to be plotted with other application

Implements several simple classifiers of sorce code:
- Linear (1 layer neural network)
- 2 layer neural network giving ~97% accuracy for 5 classes
- General N layer network

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code

Number of classes (lables) is defined automatically
"""
import sys
import os
import argparse
import pickle

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset",
                 f"{main_dir}/ModelMaker",
                 f"{main_dir}/CommonFunctions"])

from ProgramArguments import (makeArgParserCodeML, parseArguments)
from Utilities        import *
from BagTokDataset    import BagTokDataset
from DsUtilities      import DataRand
from SeqModelMaker    import SeqModelFactory

def main(args):
    """
    Main function of program for classifying source code
    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)

    if args.ckpt_dir:
        _latest_checkpoint = setupCheckpoint(args.ckpt_dir)
        _checkpoint_callback = makeCkptCallback(args.ckpt_dir)
        _callbacks=[_checkpoint_callback]
    else:
        _latest_checkpoint = None
        _callbacks = None
   
    _ds = BagTokDataset(args.dataset,
                        min_n_solutions = max(args.min_solutions, 3),
                        max_n_problems = args.problems,
                        short_code_th = args.short_code,
                        long_code_th = args.long_code,
                        test_part = args.testpart,
                        balanced_split = args.balanced_split)
    print(f"Classification of source code among {_ds.n_labels} classes")
    print("Technique of fully connected neural network on bag of tokens\n")
    _model_factory = SeqModelFactory(_ds.n_token_types, _ds.n_labels)
    if _latest_checkpoint:
        print("Restoring DNN from", _latest_checkpoint)
        _dnn = tf.keras.models.load_model(_latest_checkpoint)
    else:
        print("Constructing DNN")
        _dnn = _model_factory.denseDNN(args.dense)
    
    _val_ds, _train_ds = _ds.trainValidDs(args.valpart, args.batch)

    _history = _dnn.fit(_train_ds[0], _train_ds[1],
                        epochs = args.epochs, batch_size = args.batch,
                        validation_data = (_val_ds[0], _val_ds[1]),
                        verbose = args.progress, callbacks = _callbacks)
    with open(args.history, 'wb') as _jar:
        pickle.dump(_history.history, _jar)
    
#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nCODE CLASSIFICATION WITH BAG OF TOKENS TECHNIQUE")

    #Command-line arguments
    parser = makeArgParserCodeML(
        "Bag of tokens program source code classifier",
        task = "classification")
    args = parseArguments(parser)

    main(args)


